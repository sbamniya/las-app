"""
FuzeBox AEOS — AI Conversation Orchestrator
Manages adaptive assessment conversations with state tracking.
"""
import json
import uuid
from typing import Optional
from dataclasses import dataclass, field

from app.ai.prompts import (
    SYSTEM_PROMPT,
    PILLAR_QUESTION_BANK,
    SCORING_EXTRACTION_PROMPT,
    REPORT_NARRATIVE_PROMPT,
    RECOMMENDATION_PROMPT,
    AGENT_DEPLOYMENT_PROMPT,
)
from app.core.constants import ASSESSMENT_MODES, CAITO_PILLARS, INDUSTRY_VERTICALS
from app.scoring.caito_engine import CAITOEngine
from app.scoring.gsti_engine import GSTIEngine
from app.scoring.roi_engine import ROIEngine


@dataclass
class AssessmentState:
    """Tracks the live state of an assessment conversation."""
    assessment_id: str
    mode: str = "executive"
    transformation_goal: str = "digital_transformation"
    industry: Optional[str] = None
    current_pillar: str = "culture"
    current_depth: int = 0
    questions_asked: int = 0
    phase: str = "onboarding"  # onboarding, assessment, follow_up, scoring, reporting
    pillar_scores: dict = field(default_factory=lambda: {
        "culture": {}, "architecture": {}, "integration": {}, "talent": {}
    })
    outcomes_scores: dict = field(default_factory=dict)
    confidence_map: dict = field(default_factory=dict)
    follow_ups_pending: list = field(default_factory=list)
    conversation_history: list = field(default_factory=list)
    pillar_completion: dict = field(default_factory=lambda: {
        "culture": 0, "architecture": 0, "integration": 0, "talent": 0, "outcomes": 0
    })


class ConversationOrchestrator:
    """Orchestrates the adaptive assessment conversation."""

    def __init__(self, ai_client=None):
        self.ai_client = ai_client
        self.states: dict[str, AssessmentState] = {}

    def create_session(
        self,
        assessment_id: str,
        mode: str = "executive",
        transformation_goal: str = "digital_transformation",
        industry: Optional[str] = None,
    ) -> AssessmentState:
        state = AssessmentState(
            assessment_id=assessment_id,
            mode=mode,
            transformation_goal=transformation_goal,
            industry=industry,
        )
        self.states[assessment_id] = state
        return state

    async def process_message(self, assessment_id: str, user_message: str) -> dict:
        state = self.states.get(assessment_id)
        if not state:
            return {"error": "Session not found", "message": "Please start a new assessment."}

        state.conversation_history.append({"role": "user", "content": user_message})

        if state.phase == "onboarding":
            response = await self._handle_onboarding(state, user_message)
        elif state.phase == "assessment":
            response = await self._handle_assessment(state, user_message)
        elif state.phase == "follow_up":
            response = await self._handle_follow_up(state, user_message)
        elif state.phase == "scoring":
            response = await self._handle_scoring(state)
        elif state.phase == "reporting":
            response = await self._handle_reporting(state)
        else:
            response = await self._handle_assessment(state, user_message)

        state.conversation_history.append({"role": "assistant", "content": response["message"]})
        return response

    async def _handle_onboarding(self, state: AssessmentState, message: str) -> dict:
        lower = message.lower()

        # Detect mode selection
        if "quick" in lower:
            state.mode = "quick_scan"
        elif "deep" in lower or "diagnostic" in lower or "comprehensive" in lower:
            state.mode = "deep_diagnostic"
        elif "executive" in lower or "standard" in lower:
            state.mode = "executive"

        # Detect industry
        for key, vertical in INDUSTRY_VERTICALS.items():
            if any(word in lower for word in vertical["name"].lower().split()):
                state.industry = key
                break

        # Detect transformation goal
        goal_keywords = {
            "cost": "cost_reduction",
            "revenue": "revenue_growth",
            "automat": "automation",
            "workforce": "workforce_augmentation",
            "agent": "agent_deployment",
            "digital": "digital_transformation",
            "compliance": "compliance_governance",
        }
        for kw, goal in goal_keywords.items():
            if kw in lower:
                state.transformation_goal = goal
                break

        if state.questions_asked == 0:
            state.questions_asked = 1
            return {
                "message": (
                    "Welcome to FuzeBox AEOS Assess. I'm your AI transformation diagnostic engine.\n\n"
                    "I'll conduct a comprehensive assessment of your organization's AI readiness using "
                    "the CAITO framework — evaluating Culture, Architecture, Integration, and Talent — "
                    "and generate your Generative System Trust Index (GSTI), Return on AI (RAI), "
                    "Return on AI Agents (RAIA), and Return on Agentic Workflows (RAW) scores.\n\n"
                    "Before we begin, I need to understand your context:\n\n"
                    "1. **What industry are you in?** (Gaming/Hospitality, Healthcare, Financial Services, "
                    "Enterprise SaaS, Automotive, Higher Education, Manufacturing, or other)\n\n"
                    "2. **What is your primary transformation objective?** (Cost reduction, Revenue growth, "
                    "Automation, Workforce augmentation, Agent deployment, Digital transformation, Compliance/Governance)\n\n"
                    "3. **How deep should we go?**\n"
                    "   - **Quick Scan** (~5 min) — High-level snapshot\n"
                    "   - **Executive Assessment** (~15-20 min) — Strategic depth\n"
                    "   - **Deep Diagnostic** (~45-60 min) — Comprehensive analysis\n\n"
                    "Tell me about your organization and what brought you here today."
                ),
                "phase": "onboarding",
                "scores_updated": False,
            }

        # After initial context is gathered, move to assessment
        state.phase = "assessment"
        state.questions_asked = 0
        mode_config = ASSESSMENT_MODES[state.mode]

        industry_name = "your industry"
        if state.industry:
            industry_name = INDUSTRY_VERTICALS[state.industry]["name"]

        return {
            "message": (
                f"Excellent. I'll conduct a **{mode_config['name']}** focused on "
                f"**{state.transformation_goal.replace('_', ' ')}** for the **{industry_name}** sector.\n\n"
                f"Let's begin with **Culture** — the foundation of AI transformation.\n\n"
                f"{self._get_next_question(state)}"
            ),
            "phase": "assessment",
            "scores_updated": False,
        }

    async def _handle_assessment(self, state: AssessmentState, message: str) -> dict:
        mode_config = ASSESSMENT_MODES[state.mode]
        depth = mode_config["depth"]

        # Extract score from response
        current_pillar = state.current_pillar
        dimension = self._get_current_dimension(state)

        score_result = await self._extract_score(state, current_pillar, dimension, message)

        if score_result:
            state.pillar_scores[current_pillar][dimension] = score_result["score"]
            state.confidence_map[f"{current_pillar}.{dimension}"] = score_result["confidence"]

            if score_result.get("follow_up_needed") and state.current_depth < mode_config["follow_up_depth"]:
                state.follow_ups_pending.append({
                    "pillar": current_pillar,
                    "dimension": dimension,
                    "question": score_result.get("suggested_follow_up"),
                })

        state.questions_asked += 1
        state.pillar_completion[current_pillar] = min(
            state.questions_asked / max(mode_config["questions_per_pillar"], 1), 1.0
        )

        # Check if we need to advance pillar
        if state.questions_asked >= mode_config["questions_per_pillar"]:
            return self._advance_pillar(state)

        # Check for pending follow-ups
        if state.follow_ups_pending and depth != "surface":
            state.phase = "follow_up"
            fu = state.follow_ups_pending.pop(0)
            return {
                "message": (
                    f"I'd like to dig deeper on that.\n\n{fu['question']}"
                ),
                "phase": "follow_up",
                "scores_updated": True,
                "current_scores": self._get_current_scores(state),
            }

        next_q = self._get_next_question(state)
        return {
            "message": next_q,
            "phase": "assessment",
            "scores_updated": True,
            "current_scores": self._get_current_scores(state),
        }

    async def _handle_follow_up(self, state: AssessmentState, message: str) -> dict:
        # Process the follow-up response similarly
        current_pillar = state.current_pillar
        dimension = self._get_current_dimension(state)

        score_result = await self._extract_score(state, current_pillar, dimension, message)
        if score_result:
            # Blend with existing score
            existing = state.pillar_scores[current_pillar].get(dimension, 0.5)
            blended = existing * 0.4 + score_result["score"] * 0.6
            state.pillar_scores[current_pillar][dimension] = round(blended, 4)

        state.phase = "assessment"
        state.current_depth += 1

        mode_config = ASSESSMENT_MODES[state.mode]
        if state.questions_asked >= mode_config["questions_per_pillar"]:
            return self._advance_pillar(state)

        next_q = self._get_next_question(state)
        return {
            "message": next_q,
            "phase": "assessment",
            "scores_updated": True,
            "current_scores": self._get_current_scores(state),
        }

    def _advance_pillar(self, state: AssessmentState) -> dict:
        pillar_order = ["culture", "architecture", "integration", "talent", "outcomes"]
        current_idx = pillar_order.index(state.current_pillar)

        if current_idx < len(pillar_order) - 1:
            state.current_pillar = pillar_order[current_idx + 1]
            state.questions_asked = 0
            state.current_depth = 0
            pillar_name = CAITO_PILLARS.get(state.current_pillar, {}).get("name", state.current_pillar.title())

            transition = (
                f"Thank you. That gives me a clear picture of your **{pillar_order[current_idx].title()}** dimension.\n\n"
                f"Let's move to **{pillar_name}** — "
                f"{CAITO_PILLARS.get(state.current_pillar, {}).get('description', '')}\n\n"
                f"{self._get_next_question(state)}"
            )
            return {
                "message": transition,
                "phase": "assessment",
                "scores_updated": True,
                "current_scores": self._get_current_scores(state),
            }
        else:
            state.phase = "scoring"
            return {
                "message": (
                    "Excellent — I now have a comprehensive view across all five CAITO dimensions.\n\n"
                    "I'm computing your scores now:\n"
                    "- **CAITO Score** (AI Readiness)\n"
                    "- **GSTI** (Generative System Trust Index)\n"
                    "- **RAI** (Return on AI)\n"
                    "- **RAIA** (Return on AI Agents)\n"
                    "- **RAW** (Return on Agentic Workflows)\n\n"
                    "Generating your executive assessment report..."
                ),
                "phase": "scoring",
                "scores_updated": True,
                "current_scores": self._get_current_scores(state),
            }

    async def _handle_scoring(self, state: AssessmentState) -> dict:
        """Compute all scores and generate report."""
        caito_engine = CAITOEngine(
            transformation_goal=state.transformation_goal,
            industry=state.industry,
        )
        caito_result = caito_engine.calculate(state.pillar_scores, state.outcomes_scores or None)

        gsti_engine = GSTIEngine(
            deployment_context="agent_deployment" if state.transformation_goal == "agent_deployment" else "balanced"
        )
        gsti_result = gsti_engine.calculate(
            culture_trust=state.pillar_scores.get("culture", {}),
            architecture_trust=state.pillar_scores.get("architecture", {}),
            integration_trust=state.pillar_scores.get("integration", {}),
            talent_trust=state.pillar_scores.get("talent", {}),
        )

        state.phase = "reporting"

        scores = {
            "caito": {
                "overall": caito_result.overall_score,
                "grade": caito_result.grade,
                "pillars": {p: {"raw": ps.raw_score, "weighted": ps.weighted_score}
                            for p, ps in caito_result.pillars.items()},
                "benchmark_delta": caito_result.benchmark_delta,
            },
            "gsti": {
                "overall": gsti_result.overall_score,
                "trust_level": gsti_result.trust_level,
                "deployment_risk": gsti_result.deployment_risk,
                "autonomy_readiness": gsti_result.autonomy_readiness,
            },
            "gaps": caito_result.gaps[:5],
            "opportunities": caito_result.opportunities[:5],
        }

        return {
            "message": self._format_report(scores, state),
            "phase": "reporting",
            "scores_updated": True,
            "current_scores": scores,
        }

    async def _handle_reporting(self, state: AssessmentState) -> dict:
        return {
            "message": (
                "Your assessment is complete. You can:\n\n"
                "- **Ask questions** about any score or recommendation\n"
                "- **Run simulations** — e.g., 'What if we improve integration by 20%?'\n"
                "- **Export** your full report as PDF\n"
                "- **View the dashboard** for interactive exploration\n\n"
                "What would you like to explore?"
            ),
            "phase": "reporting",
            "scores_updated": False,
        }

    async def _extract_score(self, state: AssessmentState, pillar: str, dimension: str, response: str) -> Optional[dict]:
        """Use AI to extract a structured score from a conversational response."""
        if self.ai_client:
            prompt = SCORING_EXTRACTION_PROMPT.format(
                pillar=pillar,
                dimension=dimension,
                question=self._get_last_question(state),
                response=response,
            )
            try:
                result = await self.ai_client.generate(prompt)
                return json.loads(result)
            except Exception:
                pass

        # Fallback: heuristic scoring
        return self._heuristic_score(response)

    def _heuristic_score(self, response: str) -> dict:
        """Fallback heuristic scoring when AI is unavailable."""
        lower = response.lower()
        score = 0.5

        positive_signals = [
            "established", "mature", "robust", "comprehensive", "advanced",
            "well-defined", "integrated", "automated", "real-time", "strategic",
            "standardized", "governed", "scalable", "production", "enterprise-grade",
        ]
        negative_signals = [
            "no", "none", "haven't", "don't have", "manual", "ad hoc",
            "limited", "basic", "early", "experimenting", "struggling",
            "siloed", "fragmented", "legacy", "outdated",
        ]
        moderate_signals = [
            "some", "working on", "developing", "starting", "pilot",
            "exploring", "partially", "planning", "considering",
        ]

        pos_count = sum(1 for s in positive_signals if s in lower)
        neg_count = sum(1 for s in negative_signals if s in lower)
        mod_count = sum(1 for s in moderate_signals if s in lower)

        if pos_count > neg_count:
            score = min(0.5 + pos_count * 0.08, 0.95)
        elif neg_count > pos_count:
            score = max(0.5 - neg_count * 0.08, 0.10)
        elif mod_count > 0:
            score = 0.45

        # Length bonus: detailed responses suggest more maturity
        word_count = len(response.split())
        if word_count > 100:
            score = min(score + 0.05, 0.95)
        elif word_count < 15:
            score = max(score - 0.10, 0.10)

        confidence = min(0.3 + (word_count / 200), 0.85)

        return {
            "score": round(score, 4),
            "confidence": round(confidence, 4),
            "evidence": "Heuristic scoring based on response signals",
            "follow_up_needed": word_count < 30 or score < 0.4,
            "suggested_follow_up": "Could you elaborate on that with a specific example?" if word_count < 30 else None,
        }

    def _get_next_question(self, state: AssessmentState) -> str:
        pillar = state.current_pillar
        if pillar == "outcomes":
            pillar_key = "outcomes"
        else:
            pillar_key = pillar

        questions = PILLAR_QUESTION_BANK.get(pillar_key, {})
        depth = ASSESSMENT_MODES[state.mode]["depth"]

        if depth == "surface":
            pool = questions.get("surface", [])
        elif depth == "moderate":
            pool = questions.get("surface", []) + questions.get("moderate", [])
        else:
            pool = questions.get("surface", []) + questions.get("moderate", []) + questions.get("deep", [])

        idx = state.questions_asked % len(pool) if pool else 0
        return pool[idx] if pool else "Tell me more about your organization's approach to this area."

    def _get_current_dimension(self, state: AssessmentState) -> str:
        pillar = state.current_pillar
        if pillar in CAITO_PILLARS:
            dims = CAITO_PILLARS[pillar]["dimensions"]
            idx = state.questions_asked % len(dims)
            return dims[idx]
        return "general"

    def _get_last_question(self, state: AssessmentState) -> str:
        for msg in reversed(state.conversation_history):
            if msg["role"] == "assistant":
                return msg["content"]
        return ""

    def _get_current_scores(self, state: AssessmentState) -> dict:
        scores = {}
        for pillar, dims in state.pillar_scores.items():
            if dims:
                avg = sum(dims.values()) / len(dims)
                scores[pillar] = round(avg, 4)
        return scores

    def _format_report(self, scores: dict, state: AssessmentState) -> str:
        caito = scores["caito"]
        gsti = scores["gsti"]
        gaps = scores.get("gaps", [])
        opps = scores.get("opportunities", [])

        industry_label = ""
        if state.industry:
            industry_label = f" | Industry: {INDUSTRY_VERTICALS[state.industry]['name']}"

        report = f"""## FuzeBox AEOS Assessment Report
### AI Readiness & Agentic ROI Analysis{industry_label}

---

### CAITO Score: **{caito['overall']:.2f}** (Grade: **{caito['grade']}**)

| Pillar | Raw Score | Weighted |
|--------|-----------|----------|
| Culture | {caito['pillars'].get('culture', {}).get('raw', 0):.3f} | {caito['pillars'].get('culture', {}).get('weighted', 0):.3f} |
| Architecture | {caito['pillars'].get('architecture', {}).get('raw', 0):.3f} | {caito['pillars'].get('architecture', {}).get('weighted', 0):.3f} |
| Integration | {caito['pillars'].get('integration', {}).get('raw', 0):.3f} | {caito['pillars'].get('integration', {}).get('weighted', 0):.3f} |
| Talent | {caito['pillars'].get('talent', {}).get('raw', 0):.3f} | {caito['pillars'].get('talent', {}).get('weighted', 0):.3f} |

---

### GSTI (Trust Index): **{gsti['overall']:.2f}**
- Trust Level: **{gsti['trust_level'].title()}**
- Deployment Risk: **{gsti['deployment_risk'].title()}**
- Autonomy Readiness: **{gsti['autonomy_readiness']:.2f}**

---

### Top Gaps
"""
        for i, gap in enumerate(gaps[:5], 1):
            report += f"{i}. **{gap['pillar'].title()} → {gap['dimension'].replace('_', ' ').title()}** (Score: {gap['score']:.2f})\n"

        report += "\n### Top Opportunities\n"
        for i, opp in enumerate(opps[:5], 1):
            report += f"{i}. **{opp['pillar'].title()} → {opp['dimension'].replace('_', ' ').title()}** (Score: {opp['score']:.2f})\n"

        if caito.get("benchmark_delta"):
            report += "\n### Industry Benchmark Delta\n"
            for k, v in caito["benchmark_delta"].items():
                direction = "above" if v > 0 else "below"
                report += f"- {k.title()}: **{abs(v):.2f}** {direction} industry average\n"

        return report
