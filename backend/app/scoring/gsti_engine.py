"""
FuzeBox AEOS — GSTI (Generative System Trust Index) Engine
Same CAITO structure tuned for: deployment risk, autonomy readiness, governance maturity
GSTI = wC*Culture + wA*Architecture + wI*Integration + wT*Talent
"""
from dataclasses import dataclass, field
from typing import Optional
from app.core.constants import GSTI_WEIGHT_PRESETS, AGENT_SCORE_THRESHOLDS


@dataclass
class TrustDimension:
    name: str
    score: float
    risk_level: str  # low, medium, high, critical
    autonomy_ready: bool
    governance_maturity: str  # nascent, developing, established, advanced


@dataclass
class AgentTrustScore:
    agent_id: str
    accuracy: float
    confidence: float
    latency_normalized: float
    cost_efficiency: float
    threshold_penalties: float
    raw_score: float
    classification: str  # execute, manual_review, suppress
    grade: str


@dataclass
class GSTIResult:
    overall_score: float
    trust_level: str  # untrusted, conditional, trusted, autonomous
    pillar_trust_scores: dict[str, float]
    deployment_risk: str  # low, medium, high, critical
    autonomy_readiness: float
    governance_maturity: float
    agent_scores: list[AgentTrustScore]
    risk_flags: list[dict]
    weights_used: dict[str, float]


class GSTIEngine:
    """Generative System Trust Index — measures deployment trust and autonomy readiness."""

    def __init__(self, deployment_context: str = "balanced"):
        self.context = deployment_context
        self.weights = GSTI_WEIGHT_PRESETS.get(deployment_context, GSTI_WEIGHT_PRESETS["balanced"])

    def score_agent(
        self,
        agent_id: str,
        accuracy: float,
        confidence: float,
        latency_normalized: float,
        cost_efficiency: float,
        threshold_failures: int = 0,
    ) -> AgentTrustScore:
        """
        Agent Score = Accuracy(0.40) + Confidence(0.30) + Latency(0.15) + Cost(0.15) - Penalties
        """
        penalty = threshold_failures * 0.10
        raw = (
            accuracy * 0.40
            + confidence * 0.30
            + latency_normalized * 0.15
            + cost_efficiency * 0.15
            - penalty
        )
        raw = max(0.0, min(1.0, raw))

        if raw >= AGENT_SCORE_THRESHOLDS["execute"]:
            classification = "execute"
        elif raw >= AGENT_SCORE_THRESHOLDS["suppress"]:
            classification = "manual_review"
        else:
            classification = "suppress"

        return AgentTrustScore(
            agent_id=agent_id,
            accuracy=accuracy,
            confidence=confidence,
            latency_normalized=latency_normalized,
            cost_efficiency=cost_efficiency,
            threshold_penalties=penalty,
            raw_score=round(raw, 4),
            classification=classification,
            grade=self._grade(raw),
        )

    def calculate(
        self,
        culture_trust: dict[str, float],
        architecture_trust: dict[str, float],
        integration_trust: dict[str, float],
        talent_trust: dict[str, float],
        agent_scores: Optional[list[AgentTrustScore]] = None,
    ) -> GSTIResult:
        pillar_scores = {
            "culture": self._avg(culture_trust),
            "architecture": self._avg(architecture_trust),
            "integration": self._avg(integration_trust),
            "talent": self._avg(talent_trust),
        }

        weighted = sum(
            pillar_scores[p] * self.weights[p] for p in pillar_scores
        )

        if agent_scores:
            agent_avg = sum(a.raw_score for a in agent_scores) / len(agent_scores)
            weighted = weighted * 0.6 + agent_avg * 0.4

        overall = round(min(weighted, 1.0), 4)
        trust_level = self._trust_level(overall)
        deployment_risk = self._deployment_risk(overall, pillar_scores)
        autonomy = self._autonomy_readiness(pillar_scores, agent_scores)
        governance = self._governance_maturity(pillar_scores)
        risk_flags = self._identify_risks(pillar_scores, agent_scores)

        return GSTIResult(
            overall_score=overall,
            trust_level=trust_level,
            pillar_trust_scores=pillar_scores,
            deployment_risk=deployment_risk,
            autonomy_readiness=round(autonomy, 4),
            governance_maturity=round(governance, 4),
            agent_scores=agent_scores or [],
            risk_flags=risk_flags,
            weights_used=self.weights,
        )

    def _avg(self, scores: dict[str, float]) -> float:
        if not scores:
            return 0.0
        return round(sum(scores.values()) / len(scores), 4)

    def _trust_level(self, score: float) -> str:
        if score >= 0.80:
            return "autonomous"
        if score >= 0.60:
            return "trusted"
        if score >= 0.40:
            return "conditional"
        return "untrusted"

    def _deployment_risk(self, overall: float, pillars: dict) -> str:
        min_pillar = min(pillars.values())
        if overall < 0.35 or min_pillar < 0.25:
            return "critical"
        if overall < 0.50 or min_pillar < 0.35:
            return "high"
        if overall < 0.70 or min_pillar < 0.50:
            return "medium"
        return "low"

    def _autonomy_readiness(self, pillars: dict, agents: Optional[list]) -> float:
        base = (pillars.get("architecture", 0) * 0.35 + pillars.get("integration", 0) * 0.35 +
                pillars.get("culture", 0) * 0.15 + pillars.get("talent", 0) * 0.15)
        if agents:
            execute_pct = sum(1 for a in agents if a.classification == "execute") / len(agents)
            return base * 0.6 + execute_pct * 0.4
        return base

    def _governance_maturity(self, pillars: dict) -> float:
        return (
            pillars.get("culture", 0) * 0.30
            + pillars.get("architecture", 0) * 0.25
            + pillars.get("integration", 0) * 0.25
            + pillars.get("talent", 0) * 0.20
        )

    def _identify_risks(self, pillars: dict, agents: Optional[list]) -> list[dict]:
        risks = []
        for name, score in pillars.items():
            if score < 0.40:
                risks.append({
                    "type": "pillar_weakness",
                    "pillar": name,
                    "score": score,
                    "severity": "critical" if score < 0.25 else "high",
                    "recommendation": f"Immediate improvement needed in {name} trust dimensions",
                })
        if agents:
            suppress_count = sum(1 for a in agents if a.classification == "suppress")
            if suppress_count > 0:
                risks.append({
                    "type": "agent_suppression",
                    "count": suppress_count,
                    "severity": "high",
                    "recommendation": "Review and retrain suppressed agents before deployment",
                })
            low_confidence = [a for a in agents if a.confidence < 0.50]
            if low_confidence:
                risks.append({
                    "type": "low_confidence_agents",
                    "count": len(low_confidence),
                    "severity": "medium",
                    "recommendation": "Implement confidence calibration for flagged agents",
                })
        return risks

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
