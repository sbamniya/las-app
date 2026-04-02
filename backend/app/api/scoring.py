"""Scoring API — Direct scoring endpoints for ROI calculations."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.schemas import Assessment
from app.models.pydantic_models import (
    ROICalculationRequest, AgentScoreInput, WorkflowInput, OutcomeInput, RAIInput,
)
from app.scoring.gsti_engine import GSTIEngine
from app.scoring.roi_engine import ROIEngine, WorkflowPerformance, BusinessOutcome

router = APIRouter(prefix="/api/scoring", tags=["scoring"])


@router.post("/agent-score")
async def calculate_agent_score(agent: AgentScoreInput):
    """Calculate individual agent trust score."""
    engine = GSTIEngine()
    result = engine.score_agent(
        agent_id=agent.agent_id,
        accuracy=agent.accuracy,
        confidence=agent.confidence,
        latency_normalized=agent.latency_normalized,
        cost_efficiency=agent.cost_efficiency,
        threshold_failures=agent.threshold_failures,
    )
    return {
        "agent_id": result.agent_id,
        "raw_score": result.raw_score,
        "classification": result.classification,
        "grade": result.grade,
        "components": {
            "accuracy_contribution": round(agent.accuracy * 0.40, 4),
            "confidence_contribution": round(agent.confidence * 0.30, 4),
            "latency_contribution": round(agent.latency_normalized * 0.15, 4),
            "cost_contribution": round(agent.cost_efficiency * 0.15, 4),
            "penalties": result.threshold_penalties,
        },
    }


@router.post("/raw")
async def calculate_raw_score(
    agent_score_avg: float,
    workflow: WorkflowInput,
    outcome: OutcomeInput,
):
    """Calculate Return on Agentic Workflows (RAW)."""
    engine = ROIEngine()
    wp = WorkflowPerformance(
        completion_rate=workflow.completion_rate,
        speed_normalized=workflow.speed_normalized,
        escalation_frequency=workflow.escalation_frequency,
        human_intervention=workflow.human_intervention,
        stability=workflow.stability,
    )
    bo = BusinessOutcome(
        time_saved_normalized=outcome.time_saved_normalized,
        quality_improvement=outcome.quality_improvement,
        revenue_impact_normalized=outcome.revenue_impact_normalized,
        cost_savings_normalized=outcome.cost_savings_normalized,
    )
    result = engine.calculate_raw(agent_score_avg, wp, bo)
    return {
        "raw_score": result.raw_score,
        "grade": result.grade,
        "components": result.components,
        "workflow_performance": result.workflow_performance,
        "business_outcome_impact": result.business_outcome_impact,
    }


@router.post("/rai")
async def calculate_rai(rai: RAIInput):
    """Calculate Return on AI (RAI)."""
    engine = ROIEngine()
    result = engine.calculate_rai(
        infrastructure_cost=rai.infrastructure_cost,
        model_cost=rai.model_cost,
        human_oversight_cost=rai.human_oversight_cost,
        integration_cost=rai.integration_cost,
        revenue_generated=rai.revenue_generated,
        cost_savings=rai.cost_savings,
        productivity_gains=rai.productivity_gains,
        quality_improvements=rai.quality_improvements,
    )
    return {
        "rai_ratio": result.rai_ratio,
        "total_business_value": result.total_business_value,
        "total_investment": result.total_ai_investment,
        "investment_breakdown": result.investment_breakdown,
        "value_breakdown": result.value_breakdown,
        "payback_period_months": result.payback_period_months,
    }


@router.post("/raia")
async def calculate_raia(agents: list[dict]):
    """Calculate Return on AI Agents (RAIA)."""
    engine = ROIEngine()
    result = engine.calculate_raia(agents)
    return {
        "raia_ratio": result.raia_ratio,
        "agent_output_value": result.agent_output_value,
        "reliability": result.reliability,
        "availability": result.availability,
        "agent_cost": result.agent_cost,
        "coordination_overhead": result.coordination_overhead,
        "per_agent": result.per_agent_raia,
    }


@router.post("/full-roi")
async def calculate_full_roi(req: ROICalculationRequest, db: AsyncSession = Depends(get_db)):
    """Calculate complete ROI (RAI + RAIA + RAW + Total ROI) and save to assessment."""
    roi_engine = ROIEngine()
    gsti_engine = GSTIEngine()

    # Agent scores
    agent_trust_scores = []
    for a in req.agents:
        agent_trust_scores.append(
            gsti_engine.score_agent(a.agent_id, a.accuracy, a.confidence, a.latency_normalized, a.cost_efficiency, a.threshold_failures)
        )
    agent_avg = sum(s.raw_score for s in agent_trust_scores) / len(agent_trust_scores) if agent_trust_scores else 0

    # RAW
    wp = WorkflowPerformance(**req.workflow.model_dump())
    bo = BusinessOutcome(**req.outcome.model_dump())
    raw_result = roi_engine.calculate_raw(agent_avg, wp, bo)

    # RAI
    rai_result = roi_engine.calculate_rai(**req.rai.model_dump())

    # RAIA
    agent_details = req.agent_details or [
        {"agent_id": a.agent_id, "output_value": 1000, "reliability": a.accuracy, "availability": 0.95, "cost": 50, "coordination_overhead": 10}
        for a in req.agents
    ]
    raia_result = roi_engine.calculate_raia(agent_details)

    # Total ROI
    total = roi_engine.calculate_total_roi(raw_result, rai_result, raia_result)

    # Save to assessment
    result = await db.execute(select(Assessment).where(Assessment.id == req.assessment_id))
    assessment = result.scalar_one_or_none()
    if assessment:
        assessment.rai_score = rai_result.rai_ratio
        assessment.rai_details = {"ratio": rai_result.rai_ratio, "investment": rai_result.investment_breakdown, "value": rai_result.value_breakdown}
        assessment.raia_score = raia_result.raia_ratio
        assessment.raia_details = {"ratio": raia_result.raia_ratio, "per_agent": raia_result.per_agent_raia}
        assessment.raw_score = raw_result.raw_score
        assessment.raw_details = {"score": raw_result.raw_score, "grade": raw_result.grade, "components": raw_result.components}
        assessment.total_roi = total.total_roi
        assessment.total_roi_details = {
            "total": total.total_roi, "hitl": total.hitl_score,
            "agent_roi": total.agent_roi, "synergy": total.synergy_factor,
            "coordination_tax": total.coordination_tax, "grade": total.grade,
        }
        await db.commit()

    return {
        "total_roi": total.total_roi,
        "grade": total.grade,
        "hitl_score": total.hitl_score,
        "agent_roi": total.agent_roi,
        "synergy_factor": total.synergy_factor,
        "coordination_tax": total.coordination_tax,
        "raw": {"score": raw_result.raw_score, "grade": raw_result.grade, "components": raw_result.components},
        "rai": {"ratio": rai_result.rai_ratio, "payback_months": rai_result.payback_period_months},
        "raia": {"ratio": raia_result.raia_ratio, "per_agent": raia_result.per_agent_raia},
        "agent_trust_scores": [
            {"agent_id": s.agent_id, "score": s.raw_score, "classification": s.classification, "grade": s.grade}
            for s in agent_trust_scores
        ],
    }
