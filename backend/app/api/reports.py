"""Report generation API."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.schemas import Assessment, Organization
from app.models.pydantic_models import ReportRequest
from app.ai.client import AIClient
from app.ai.prompts import REPORT_NARRATIVE_PROMPT, RECOMMENDATION_PROMPT, AGENT_DEPLOYMENT_PROMPT
from app.core.constants import INDUSTRY_VERTICALS

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate")
async def generate_report(req: ReportRequest, db: AsyncSession = Depends(get_db)):
    """Generate comprehensive assessment report."""
    result = await db.execute(select(Assessment).where(Assessment.id == req.assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    org_result = await db.execute(select(Organization).where(Organization.id == assessment.organization_id))
    org = org_result.scalar_one_or_none()

    report = {
        "organization": {
            "name": org.name if org else "Unknown",
            "industry": org.industry if org else None,
            "size": org.size if org else None,
        },
        "assessment": {
            "id": str(assessment.id),
            "mode": assessment.mode,
            "transformation_goal": assessment.transformation_goal,
            "status": assessment.status,
            "started_at": str(assessment.started_at),
            "completed_at": str(assessment.completed_at) if assessment.completed_at else None,
        },
        "scores": {
            "caito": {
                "score": assessment.caito_score,
                "grade": assessment.caito_grade,
                "details": assessment.caito_details,
            },
            "gsti": {
                "score": assessment.gsti_score,
                "details": assessment.gsti_details,
            },
            "rai": {
                "score": assessment.rai_score,
                "details": assessment.rai_details,
            },
            "raia": {
                "score": assessment.raia_score,
                "details": assessment.raia_details,
            },
            "raw": {
                "score": assessment.raw_score,
                "details": assessment.raw_details,
            },
            "total_roi": {
                "score": assessment.total_roi,
                "details": assessment.total_roi_details,
            },
        },
        "analysis": {
            "gaps": assessment.gaps or [],
            "opportunities": assessment.opportunities or [],
            "recommendations": assessment.recommendations or {},
            "roadmap": assessment.roadmap or {},
            "agent_deployment_plan": assessment.agent_deployment_plan or {},
        },
    }

    # Generate AI narrative if requested
    try:
        ai = AIClient()
        caito_details = assessment.caito_details or {}
        pillars = caito_details.get("pillars", {})

        narrative = await ai.generate(
            REPORT_NARRATIVE_PROMPT.format(
                org_name=org.name if org else "Organization",
                industry=org.industry if org else "General",
                caito_score=assessment.caito_score or 0,
                caito_grade=assessment.caito_grade or "N/A",
                culture_score=pillars.get("culture", {}).get("raw", 0),
                architecture_score=pillars.get("architecture", {}).get("raw", 0),
                integration_score=pillars.get("integration", {}).get("raw", 0),
                talent_score=pillars.get("talent", {}).get("raw", 0),
                gsti_score=assessment.gsti_score or 0,
                trust_level=(assessment.gsti_details or {}).get("trust_level", "N/A"),
                deployment_risk=(assessment.gsti_details or {}).get("deployment_risk", "N/A"),
                rai_ratio=assessment.rai_score or 0,
                raia_ratio=assessment.raia_score or 0,
                raw_score=assessment.raw_score or 0,
                gaps=assessment.gaps or [],
                opportunities=assessment.opportunities or [],
            )
        )
        report["narrative"] = narrative
    except Exception:
        report["narrative"] = None

    return JSONResponse(content=report)


@router.post("/recommendations")
async def generate_recommendations(assessment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Generate AI-powered recommendations."""
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment_data = {
        "caito_score": assessment.caito_score,
        "caito_details": assessment.caito_details,
        "gsti_score": assessment.gsti_score,
        "gsti_details": assessment.gsti_details,
        "gaps": assessment.gaps,
        "opportunities": assessment.opportunities,
        "transformation_goal": assessment.transformation_goal,
    }

    try:
        ai = AIClient()
        recs = await ai.generate_json(RECOMMENDATION_PROMPT.format(assessment_json=str(assessment_data)))
        assessment.recommendations = recs
        await db.commit()
        return recs
    except Exception as e:
        # Fallback static recommendations
        return _generate_fallback_recommendations(assessment_data)


@router.post("/agent-deployment-plan")
async def generate_agent_deployment_plan(assessment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Generate agent deployment plan."""
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    org_result = await db.execute(select(Organization).where(Organization.id == assessment.organization_id))
    org = org_result.scalar_one_or_none()

    industry = org.industry if org else None
    workflows = []
    if industry and industry in INDUSTRY_VERTICALS:
        workflows = INDUSTRY_VERTICALS[industry]["key_workflows"]

    assessment_data = {
        "caito_score": assessment.caito_score,
        "gsti_score": assessment.gsti_score,
        "raw_score": assessment.raw_score,
        "gaps": assessment.gaps,
    }

    try:
        ai = AIClient()
        plan = await ai.generate_json(
            AGENT_DEPLOYMENT_PROMPT.format(
                assessment_json=str(assessment_data),
                industry=industry or "General",
                workflows=workflows,
            )
        )
        assessment.agent_deployment_plan = plan
        await db.commit()
        return plan
    except Exception:
        return _generate_fallback_deployment_plan(workflows)


def _generate_fallback_recommendations(data: dict) -> dict:
    gaps = data.get("gaps", [])
    return {
        "immediate": [
            {
                "action": f"Address {g['dimension'].replace('_', ' ')} gap in {g['pillar']}",
                "impact": "high" if g.get("priority", 0) > 2 else "medium",
                "investment": "low",
                "timeline": "0-30 days",
            }
            for g in gaps[:3]
        ],
        "mid_term": [
            {"action": "Implement AI governance framework", "impact": "high", "investment": "medium", "timeline": "30-90 days"},
            {"action": "Launch AI literacy training program", "impact": "medium", "investment": "medium", "timeline": "30-90 days"},
        ],
        "strategic": [
            {"action": "Deploy enterprise AI decision infrastructure", "impact": "transformative", "investment": "high", "timeline": "90+ days"},
            {"action": "Implement agentic workflow automation", "impact": "high", "investment": "high", "timeline": "90+ days"},
        ],
    }


def _generate_fallback_deployment_plan(workflows: list) -> dict:
    return {
        "recommended_workflows": [
            {
                "workflow": wf.replace("_", " ").title(),
                "priority": i + 1,
                "expected_raia": round(0.85 - i * 0.05, 2),
                "timeline": f"{(i + 1) * 4} weeks",
                "infrastructure_needed": ["API integration", "AI model access", "Data pipeline"],
            }
            for i, wf in enumerate(workflows[:5])
        ],
    }
