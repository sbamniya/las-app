"""Assessment API routes."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.schemas import Organization, Assessment, AssessmentResponse as ARModel, Conversation, Message
from app.models.pydantic_models import (
    OrganizationCreate, OrganizationResponse,
    AssessmentCreate, AssessmentResponse, AssessmentDetail,
    ManualScoreInput, SimulationRequest, SimulationResponse,
)
from app.scoring.caito_engine import CAITOEngine
from app.scoring.gsti_engine import GSTIEngine

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.post("/organizations", response_model=OrganizationResponse)
async def create_organization(org: OrganizationCreate, db: AsyncSession = Depends(get_db)):
    db_org = Organization(**org.model_dump())
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    return db_org


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(org_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.post("/", response_model=AssessmentResponse)
async def create_assessment(req: AssessmentCreate, db: AsyncSession = Depends(get_db)):
    assessment = Assessment(
        organization_id=req.organization_id,
        mode=req.mode,
        transformation_goal=req.transformation_goal,
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment


@router.get("/{assessment_id}", response_model=AssessmentDetail)
async def get_assessment(assessment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.get("/organization/{org_id}", response_model=list[AssessmentResponse])
async def list_assessments(org_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Assessment).where(Assessment.organization_id == org_id).order_by(Assessment.started_at.desc())
    )
    return result.scalars().all()


@router.post("/score", response_model=AssessmentDetail)
async def score_assessment(req: ManualScoreInput, db: AsyncSession = Depends(get_db)):
    """Manually trigger scoring for an assessment with provided pillar scores."""
    result = await db.execute(select(Assessment).where(Assessment.id == req.assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    engine = CAITOEngine(
        transformation_goal=assessment.transformation_goal,
        industry=None,  # Will be resolved from org
    )
    caito_result = engine.calculate(req.pillar_scores, req.outcomes_scores)

    assessment.caito_score = caito_result.overall_score
    assessment.caito_grade = caito_result.grade
    assessment.caito_details = {
        "pillars": {p: {"raw": ps.raw_score, "weighted": ps.weighted_score, "weight": ps.weight}
                    for p, ps in caito_result.pillars.items()},
        "weights": caito_result.weights_used,
        "confidence": caito_result.confidence,
    }
    assessment.gaps = [dict(g) for g in caito_result.gaps]
    assessment.opportunities = [dict(o) for o in caito_result.opportunities]

    # GSTI
    gsti_engine = GSTIEngine()
    gsti_result = gsti_engine.calculate(
        culture_trust=req.pillar_scores.get("culture", {}),
        architecture_trust=req.pillar_scores.get("architecture", {}),
        integration_trust=req.pillar_scores.get("integration", {}),
        talent_trust=req.pillar_scores.get("talent", {}),
    )
    assessment.gsti_score = gsti_result.overall_score
    assessment.gsti_details = {
        "trust_level": gsti_result.trust_level,
        "deployment_risk": gsti_result.deployment_risk,
        "autonomy_readiness": gsti_result.autonomy_readiness,
        "governance_maturity": gsti_result.governance_maturity,
    }

    assessment.status = "completed"
    await db.commit()
    await db.refresh(assessment)
    return assessment


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_changes(req: SimulationRequest, db: AsyncSession = Depends(get_db)):
    """Simulate: 'What happens if Integration improves by 20%?'"""
    result = await db.execute(select(Assessment).where(Assessment.id == req.assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if not assessment.caito_details:
        raise HTTPException(status_code=400, detail="Assessment has not been scored yet")

    engine = CAITOEngine(transformation_goal=assessment.transformation_goal)

    # Reconstruct current pillar scores from stored details
    current_scores = {}
    for pillar_name, pillar_data in assessment.caito_details.get("pillars", {}).items():
        current_scores[pillar_name] = {dim: pillar_data.get("raw", 0.5) for dim in ["general"]}

    # Apply simulation
    original = engine.calculate(current_scores)
    simulated = engine.simulate(original, req.changes)

    pillar_deltas = {}
    for p in ["culture", "architecture", "integration", "talent"]:
        orig_p = original.pillars.get(p)
        sim_p = simulated.pillars.get(p)
        if orig_p and sim_p:
            pillar_deltas[p] = round(sim_p.raw_score - orig_p.raw_score, 4)

    return SimulationResponse(
        original_caito=original.overall_score,
        simulated_caito=simulated.overall_score,
        delta=round(simulated.overall_score - original.overall_score, 4),
        pillar_deltas=pillar_deltas,
    )
