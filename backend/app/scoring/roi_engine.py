"""
FuzeBox AEOS — ROI Scoring Engine
RAI  = Return on AI
RAIA = Return on AI Agents
RAW  = Return on Agentic Workflows
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WorkflowPerformance:
    completion_rate: float  # 1.0/0.5/0.0
    speed_normalized: float  # vs baseline target
    escalation_frequency: float  # 1.0 if none
    human_intervention: float  # 1.0 if none
    stability: float  # 1.0 - 0.25/re-run

    @property
    def score(self) -> float:
        return round(
            self.completion_rate * 0.40
            + self.speed_normalized * 0.30
            + self.escalation_frequency * 0.15
            + self.human_intervention * 0.10
            + self.stability * 0.05,
            4,
        )


@dataclass
class BusinessOutcome:
    time_saved_normalized: float  # min/60
    quality_improvement: float  # 0-1
    revenue_impact_normalized: float  # $/1000
    cost_savings_normalized: float  # $/500

    @property
    def score(self) -> float:
        return round(
            self.time_saved_normalized * 0.30
            + self.quality_improvement * 0.20
            + self.revenue_impact_normalized * 0.30
            + self.cost_savings_normalized * 0.20,
            4,
        )


@dataclass
class RAWResult:
    """Return on Agentic Workflows"""
    agent_score_avg: float
    workflow_performance: float
    business_outcome_impact: float
    raw_score: float
    grade: str
    components: dict


@dataclass
class RAIResult:
    """Return on AI"""
    total_business_value: float
    total_ai_investment: float
    rai_ratio: float
    investment_breakdown: dict
    value_breakdown: dict
    payback_period_months: Optional[float] = None


@dataclass
class RAIAResult:
    """Return on AI Agents"""
    agent_output_value: float
    reliability: float
    availability: float
    agent_cost: float
    coordination_overhead: float
    raia_ratio: float
    per_agent_raia: list[dict] = field(default_factory=list)


@dataclass
class TotalROIResult:
    """Combined ROI across all dimensions"""
    hitl_score: float  # Human in the Loop
    agent_roi: float
    synergy_factor: float
    coordination_tax: float
    total_roi: float
    raw: RAWResult
    rai: RAIResult
    raia: RAIAResult
    grade: str


class ROIEngine:
    """Complete ROI calculation engine for AI, Agents, and Agentic Workflows."""

    def calculate_raw(
        self,
        agent_score_avg: float,
        workflow: WorkflowPerformance,
        outcome: BusinessOutcome,
    ) -> RAWResult:
        """
        RAW = (Agent Score * 0.30) + (Workflow Performance * 0.30) + (Business Outcome * 0.40)
        """
        wp = workflow.score
        bo = outcome.score
        raw_val = agent_score_avg * 0.30 + wp * 0.30 + bo * 0.40
        raw_val = round(min(raw_val, 1.0), 4)

        return RAWResult(
            agent_score_avg=round(agent_score_avg, 4),
            workflow_performance=wp,
            business_outcome_impact=bo,
            raw_score=raw_val,
            grade=self._grade(raw_val),
            components={
                "agent_contribution": round(agent_score_avg * 0.30, 4),
                "workflow_contribution": round(wp * 0.30, 4),
                "outcome_contribution": round(bo * 0.40, 4),
            },
        )

    def calculate_rai(
        self,
        infrastructure_cost: float,
        model_cost: float,
        human_oversight_cost: float,
        integration_cost: float,
        revenue_generated: float,
        cost_savings: float,
        productivity_gains: float,
        quality_improvements: float,
        monthly: bool = True,
    ) -> RAIResult:
        """
        RAI = Total Business Value Created / Total AI Investment
        """
        total_investment = infrastructure_cost + model_cost + human_oversight_cost + integration_cost
        total_value = revenue_generated + cost_savings + productivity_gains + quality_improvements

        ratio = total_value / total_investment if total_investment > 0 else 0.0
        payback = None
        if monthly and total_value > 0:
            payback = round(total_investment / (total_value / 12), 1) if total_value > 0 else None

        return RAIResult(
            total_business_value=round(total_value, 2),
            total_ai_investment=round(total_investment, 2),
            rai_ratio=round(ratio, 4),
            investment_breakdown={
                "infrastructure": infrastructure_cost,
                "model_costs": model_cost,
                "human_oversight": human_oversight_cost,
                "integration": integration_cost,
            },
            value_breakdown={
                "revenue_generated": revenue_generated,
                "cost_savings": cost_savings,
                "productivity_gains": productivity_gains,
                "quality_improvements": quality_improvements,
            },
            payback_period_months=payback,
        )

    def calculate_raia(
        self,
        agents: list[dict],
    ) -> RAIAResult:
        """
        RAIA = (Agent Output Value * Reliability * Availability) / (Agent Cost + Coordination Overhead)
        agents: list of {output_value, reliability, availability, cost, coordination_overhead}
        """
        total_output = 0.0
        total_reliability = 0.0
        total_availability = 0.0
        total_cost = 0.0
        total_overhead = 0.0
        per_agent = []

        for agent in agents:
            ov = agent["output_value"]
            r = agent["reliability"]
            a = agent["availability"]
            c = agent["cost"]
            co = agent.get("coordination_overhead", 0)

            numerator = ov * r * a
            denominator = c + co
            individual_raia = numerator / denominator if denominator > 0 else 0

            total_output += ov
            total_reliability += r
            total_availability += a
            total_cost += c
            total_overhead += co

            per_agent.append({
                "agent_id": agent.get("agent_id", "unknown"),
                "output_value": ov,
                "reliability": r,
                "availability": a,
                "cost": c,
                "raia": round(individual_raia, 4),
            })

        n = len(agents) if agents else 1
        avg_reliability = total_reliability / n
        avg_availability = total_availability / n

        overall_num = total_output * avg_reliability * avg_availability
        overall_den = total_cost + total_overhead
        overall_raia = overall_num / overall_den if overall_den > 0 else 0

        return RAIAResult(
            agent_output_value=round(total_output, 2),
            reliability=round(avg_reliability, 4),
            availability=round(avg_availability, 4),
            agent_cost=round(total_cost, 2),
            coordination_overhead=round(total_overhead, 2),
            raia_ratio=round(overall_raia, 4),
            per_agent_raia=per_agent,
        )

    def calculate_total_roi(
        self,
        raw_result: RAWResult,
        rai_result: RAIResult,
        raia_result: RAIAResult,
        coordination_tax: float = 0.25,
        human_factors: Optional[dict] = None,
    ) -> TotalROIResult:
        """
        Total ROI = HITL + Agent ROI + Synergy - Coordination Tax
        HITL = T * C * J * K * A * (1 - F)
        Agent ROI = P * R * V
        Synergy = (L * E * D * M) - B
        """
        hf = human_factors or {
            "time_efficiency": 0.80, "cognitive_load": 0.75,
            "judgment_quality": 0.85, "knowledge_access": 0.90,
            "adaptability": 0.80, "fatigue_factor": 0.25,
        }
        hitl = (
            hf["time_efficiency"]
            * hf["cognitive_load"]
            * hf["judgment_quality"]
            * hf["knowledge_access"]
            * hf["adaptability"]
            * (1 - hf["fatigue_factor"])
        )

        processing = min(raw_result.agent_score_avg, 1.0)
        agent_roi_val = processing * raia_result.reliability * raia_result.availability

        synergy_factors = {
            "learning": 0.72, "engagement": 0.68,
            "data_quality": 0.75, "maturity": 0.60, "bias": 0.15,
        }
        synergy = (
            synergy_factors["learning"]
            * synergy_factors["engagement"]
            * synergy_factors["data_quality"]
            * synergy_factors["maturity"]
        ) - synergy_factors["bias"]

        total = hitl + agent_roi_val + synergy
        total *= (1 - coordination_tax)

        return TotalROIResult(
            hitl_score=round(hitl, 4),
            agent_roi=round(agent_roi_val, 4),
            synergy_factor=round(synergy, 4),
            coordination_tax=coordination_tax,
            total_roi=round(total, 4),
            raw=raw_result,
            rai=rai_result,
            raia=raia_result,
            grade=self._grade(min(total, 1.0)),
        )

    def _grade(self, score: float) -> str:
        if score >= 0.90:
            return "A"
        if score >= 0.80:
            return "B"
        if score >= 0.70:
            return "C"
        if score >= 0.60:
            return "D"
        return "F"
