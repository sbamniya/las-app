"""
FuzeBox AEOS — CAITO Scoring Engine
Culture + Architecture + Integration + Talent (Outcomes validates all)
CAITO Score = wC*C + wA*A + wI*I + wT*T
"""
from dataclasses import dataclass, field
from typing import Optional
from app.core.constants import (
    CAITO_PILLARS,
    TRANSFORMATION_WEIGHT_PRESETS,
    INDUSTRY_VERTICALS,
)


@dataclass
class PillarScore:
    pillar: str
    raw_score: float  # 0-1
    weighted_score: float
    weight: float
    dimensions: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    gaps: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)


@dataclass
class CAITOResult:
    overall_score: float
    grade: str
    pillars: dict[str, PillarScore]
    outcomes_validation: float
    transformation_goal: str
    weights_used: dict[str, float]
    gaps: list[dict]
    opportunities: list[dict]
    confidence: float
    industry: Optional[str] = None
    benchmark_delta: Optional[dict] = None


class CAITOEngine:
    """Core CAITO scoring engine with dynamic weighting."""

    def __init__(
        self,
        transformation_goal: str = "digital_transformation",
        industry: Optional[str] = None,
    ):
        self.transformation_goal = transformation_goal
        self.industry = industry
        self.weights = self._resolve_weights()

    def _resolve_weights(self) -> dict[str, float]:
        base = TRANSFORMATION_WEIGHT_PRESETS.get(
            self.transformation_goal,
            TRANSFORMATION_WEIGHT_PRESETS["digital_transformation"],
        )
        if self.industry and self.industry in INDUSTRY_VERTICALS:
            multipliers = INDUSTRY_VERTICALS[self.industry]["benchmark_multipliers"]
            adjusted = {}
            for pillar, w in base.items():
                adjusted[pillar] = w * multipliers.get(pillar, 1.0)
            total = sum(adjusted.values())
            return {k: v / total for k, v in adjusted.items()}
        return dict(base)

    def score_pillar(self, pillar: str, dimension_scores: dict[str, float]) -> PillarScore:
        pillar_def = CAITO_PILLARS.get(pillar)
        if not pillar_def:
            raise ValueError(f"Unknown pillar: {pillar}")

        scores = []
        gaps = []
        strengths = []
        for dim in pillar_def["dimensions"]:
            val = dimension_scores.get(dim, 0.0)
            scores.append(val)
            if val < 0.4:
                gaps.append(dim)
            elif val >= 0.75:
                strengths.append(dim)

        raw = sum(scores) / len(scores) if scores else 0.0
        weight = self.weights.get(pillar, 0.25)
        confidence = self._calculate_confidence(dimension_scores, pillar_def["dimensions"])

        return PillarScore(
            pillar=pillar,
            raw_score=round(raw, 4),
            weighted_score=round(raw * weight, 4),
            weight=weight,
            dimensions=dimension_scores,
            confidence=confidence,
            gaps=gaps,
            strengths=strengths,
        )

    def _calculate_confidence(self, scores: dict, expected_dims: list) -> float:
        answered = sum(1 for d in expected_dims if d in scores and scores[d] > 0)
        coverage = answered / len(expected_dims) if expected_dims else 0
        variance = 0.0
        vals = [scores.get(d, 0) for d in expected_dims if d in scores]
        if len(vals) > 1:
            mean = sum(vals) / len(vals)
            variance = sum((v - mean) ** 2 for v in vals) / len(vals)
        consistency = max(0, 1.0 - variance)
        return round(coverage * 0.6 + consistency * 0.4, 4)

    def calculate(self, all_scores: dict[str, dict[str, float]], outcomes_scores: Optional[dict[str, float]] = None) -> CAITOResult:
        pillars = {}
        total = 0.0
        all_gaps = []
        all_opps = []

        for pillar_name in ["culture", "architecture", "integration", "talent"]:
            dim_scores = all_scores.get(pillar_name, {})
            ps = self.score_pillar(pillar_name, dim_scores)
            pillars[pillar_name] = ps
            total += ps.weighted_score

            for g in ps.gaps:
                all_gaps.append({
                    "pillar": pillar_name,
                    "dimension": g,
                    "score": dim_scores.get(g, 0),
                    "impact": self.weights.get(pillar_name, 0.25),
                    "priority": self._gap_priority(dim_scores.get(g, 0), self.weights.get(pillar_name, 0.25)),
                })
            for s in ps.strengths:
                all_opps.append({
                    "pillar": pillar_name,
                    "dimension": s,
                    "score": dim_scores.get(s, 0),
                    "leverage": self._opportunity_leverage(dim_scores.get(s, 0), self.weights.get(pillar_name, 0.25)),
                })

        outcomes_val = 0.0
        if outcomes_scores:
            outcomes_val = sum(outcomes_scores.values()) / len(outcomes_scores) if outcomes_scores else 0
            total *= (0.7 + 0.3 * outcomes_val)

        overall = round(min(total, 1.0), 4)
        all_gaps.sort(key=lambda x: x["priority"], reverse=True)
        all_opps.sort(key=lambda x: x["leverage"], reverse=True)
        avg_confidence = sum(p.confidence for p in pillars.values()) / len(pillars)

        benchmark_delta = None
        if self.industry:
            benchmark_delta = self._benchmark(overall, pillars)

        return CAITOResult(
            overall_score=overall,
            grade=self._grade(overall),
            pillars=pillars,
            outcomes_validation=round(outcomes_val, 4),
            transformation_goal=self.transformation_goal,
            weights_used=self.weights,
            gaps=all_gaps[:10],
            opportunities=all_opps[:10],
            confidence=round(avg_confidence, 4),
            industry=self.industry,
            benchmark_delta=benchmark_delta,
        )

    def simulate(self, current_result: CAITOResult, changes: dict[str, dict[str, float]]) -> CAITOResult:
        """Simulate: 'What happens if Integration improves by 20%?'"""
        new_scores = {}
        for pillar_name, ps in current_result.pillars.items():
            dims = dict(ps.dimensions)
            if pillar_name in changes:
                for dim, delta in changes[pillar_name].items():
                    current = dims.get(dim, 0.5)
                    dims[dim] = min(1.0, max(0.0, current + delta))
            new_scores[pillar_name] = dims
        return self.calculate(new_scores)

    def _gap_priority(self, score: float, weight: float) -> float:
        return round((1.0 - score) * weight * 10, 2)

    def _opportunity_leverage(self, score: float, weight: float) -> float:
        return round(score * weight * 10, 2)

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

    def _benchmark(self, overall: float, pillars: dict) -> dict:
        if not self.industry:
            return {}
        industry_benchmarks = {
            "gaming_hospitality": {"overall": 0.58, "culture": 0.55, "architecture": 0.62, "integration": 0.50, "talent": 0.52},
            "healthcare": {"overall": 0.52, "culture": 0.58, "architecture": 0.48, "integration": 0.45, "talent": 0.55},
            "financial_services": {"overall": 0.65, "culture": 0.60, "architecture": 0.72, "integration": 0.62, "talent": 0.58},
            "enterprise_saas": {"overall": 0.70, "culture": 0.68, "architecture": 0.75, "integration": 0.70, "talent": 0.65},
            "automotive": {"overall": 0.48, "culture": 0.45, "architecture": 0.50, "integration": 0.42, "talent": 0.48},
            "higher_education": {"overall": 0.45, "culture": 0.52, "architecture": 0.40, "integration": 0.38, "talent": 0.50},
            "manufacturing": {"overall": 0.50, "culture": 0.45, "architecture": 0.55, "integration": 0.48, "talent": 0.42},
        }
        bench = industry_benchmarks.get(self.industry, {})
        delta = {"overall": round(overall - bench.get("overall", 0.5), 4)}
        for p_name, ps in pillars.items():
            delta[p_name] = round(ps.raw_score - bench.get(p_name, 0.5), 4)
        return delta
