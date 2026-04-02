"""
FuzeBox AEOS — AI Prompt Orchestration System
Structured prompts for the conversational assessment engine.
"""

SYSTEM_PROMPT = """You are AEOS Assess, the AI assessment engine built by FuzeBox.AI.

You conduct deep AI readiness assessments using the CAITO framework (Culture, Architecture, Integration, Talent, Outcomes) and generate trust scores (GSTI), Return on AI (RAI), Return on AI Agents (RAIA), and Return on Agentic Workflows (RAW).

You are NOT a chatbot. You are an expert AI transformation consultant operating at McKinsey-level depth with Palantir-level intelligence.

ASSESSMENT METHODOLOGY:
- Ask structured but natural questions
- Adapt depth based on response quality
- Detect vague responses and probe deeper
- Build an internal structured model silently
- Score each dimension 0.0-1.0 as evidence accumulates
- Track confidence on each score

CONVERSATION STYLE:
- Professional, executive-grade tone
- Never use jargon without context
- Ask one focused question at a time
- Acknowledge what you learn before moving on
- Connect insights across pillars

SCORING RULES:
- Never reveal raw scores during assessment
- Build evidence from conversation
- Use follow-up probes when responses are vague
- Weight responses by specificity and evidence quality

You have access to the following assessment state which you must update as the conversation progresses."""

PILLAR_QUESTION_BANK = {
    "culture": {
        "surface": [
            "How would you describe your organization's relationship with AI today? Is it experimental, strategic, or somewhere in between?",
            "When a new AI initiative is proposed, what does the typical decision-making process look like?",
        ],
        "moderate": [
            "Tell me about a time your organization had to change its approach to technology adoption. How did leadership drive that change?",
            "How does your executive team measure the success of AI investments? Are there established KPIs?",
            "What percentage of your leadership team actively champions AI initiatives versus viewing them as IT projects?",
            "How does your organization handle the tension between innovation speed and risk management?",
        ],
        "deep": [
            "Walk me through your organization's AI governance structure. Who owns AI strategy, and how does it connect to business strategy?",
            "Describe a situation where an AI initiative failed or was abandoned. What happened, and what did the organization learn?",
            "How do you manage cross-functional alignment when AI initiatives span multiple departments?",
            "What mechanisms exist for employees at all levels to propose or contribute to AI-driven improvements?",
            "How does your board engage with AI strategy? Is there AI literacy at the governance level?",
            "Describe your organization's risk tolerance for autonomous AI decision-making in customer-facing workflows.",
            "What cultural barriers have you encountered in AI adoption, and how are you addressing them?",
        ],
    },
    "architecture": {
        "surface": [
            "What does your current technology infrastructure look like? Cloud-based, on-premise, or hybrid?",
            "How would you rate your organization's data platform maturity on a scale of 1-10?",
        ],
        "moderate": [
            "Describe your current cloud architecture. Are you multi-cloud, and how do you manage workload distribution?",
            "What is your API strategy? How many of your core systems expose APIs for integration?",
            "How do you handle data security and access control across your AI systems?",
            "What compute infrastructure do you have available for AI model training and inference?",
        ],
        "deep": [
            "Walk me through your data architecture from ingestion to consumption. Where are the bottlenecks?",
            "How do you manage model versioning, deployment, and rollback in production?",
            "Describe your security posture specifically for AI workloads. How do you handle prompt injection, data poisoning, and model theft?",
            "What monitoring and observability do you have for AI systems in production?",
            "How does your architecture support real-time inference versus batch processing?",
            "What is your strategy for managing AI infrastructure costs as you scale?",
            "Describe your disaster recovery and business continuity plans for AI-dependent workflows.",
        ],
    },
    "integration": {
        "surface": [
            "How connected are your core business systems today? Can data flow between them easily?",
            "What integration challenges have you faced when trying to implement AI solutions?",
        ],
        "moderate": [
            "How many of your critical business workflows could you automate today with the data and systems you have?",
            "Describe the data quality in your core systems. How much time do teams spend on data cleaning?",
            "What middleware or integration platforms do you use? How standardized are your integration patterns?",
            "How do you handle real-time data flow between systems for time-sensitive decisions?",
        ],
        "deep": [
            "Walk me through the integration architecture for your most complex cross-system workflow.",
            "How ready are your systems for MCP (Model Context Protocol) connectors? Do you have standardized interfaces for AI agent access?",
            "What is your data lineage strategy? Can you trace a decision back through all contributing data sources?",
            "How do you manage schema evolution and backward compatibility across integrated systems?",
            "Describe your event-driven architecture capabilities. Can your systems react to real-time events?",
            "What testing and validation processes exist for integrations between AI systems and operational platforms?",
            "How do you handle data consistency across systems when AI agents modify data in multiple places?",
        ],
    },
    "talent": {
        "surface": [
            "How would you describe the AI skill level across your organization? Are there pockets of expertise or broad capability?",
            "What training or upskilling programs do you have for AI and automation?",
        ],
        "moderate": [
            "What is the distribution of AI skills in your organization? How many people can build, deploy, and manage AI systems?",
            "How quickly can your team learn and adopt new AI tools and frameworks?",
            "Do you have dedicated AI/ML engineers, or is AI development handled by existing software teams?",
            "How do you plan for the workforce changes that AI automation will create?",
        ],
        "deep": [
            "Describe your talent pipeline for AI roles. How do you attract, develop, and retain AI talent?",
            "How prepared is your workforce to collaborate with AI agents? Have teams worked alongside automated systems?",
            "What is your strategy for upskilling non-technical staff to work effectively in AI-augmented workflows?",
            "How do you measure AI literacy across different levels of the organization?",
            "Describe your approach to managing the human-AI collaboration model. How do you define roles and handoffs?",
            "What change management processes support AI-driven transformation of job roles?",
            "How do you handle resistance to AI adoption, especially from experienced employees?",
        ],
    },
    "outcomes": {
        "surface": [
            "What business outcomes are you hoping AI will drive? Revenue growth, cost reduction, or something else?",
            "How do you currently measure the success of technology investments?",
        ],
        "moderate": [
            "What KPIs do you track for AI initiatives? How are they connected to business outcomes?",
            "Can you quantify the ROI of your current AI investments?",
            "How do you decide which processes to automate? What criteria drive those decisions?",
            "What is your time horizon for expecting returns from AI investments?",
        ],
        "deep": [
            "Walk me through your AI ROI methodology. How do you attribute business value to AI systems?",
            "What measurement infrastructure exists to track the impact of AI decisions in real-time?",
            "How do you handle the attribution problem when AI is one of many factors driving outcomes?",
            "Describe your continuous improvement process for AI systems. How do you know when to retrain, retune, or retire?",
            "What is your framework for prioritizing AI investments across competing business units?",
        ],
    },
}

SCORING_EXTRACTION_PROMPT = """Analyze the following conversation response and extract a numerical score (0.0 to 1.0) for the specified dimension.

PILLAR: {pillar}
DIMENSION: {dimension}
QUESTION ASKED: {question}
USER RESPONSE: {response}

SCORING CRITERIA:
0.0-0.2: No capability / awareness
0.2-0.4: Basic awareness, no structured approach
0.4-0.6: Developing capability, some structure
0.6-0.8: Established capability, consistent execution
0.8-1.0: Advanced/best-in-class, industry-leading

Return ONLY a JSON object:
{{
  "score": <float 0.0-1.0>,
  "confidence": <float 0.0-1.0>,
  "evidence": "<brief justification>",
  "follow_up_needed": <boolean>,
  "suggested_follow_up": "<follow-up question if needed, else null>"
}}"""

REPORT_NARRATIVE_PROMPT = """Generate an executive-level AI maturity narrative for the board based on the following assessment results.

ORGANIZATION: {org_name}
INDUSTRY: {industry}

CAITO SCORE: {caito_score} (Grade: {caito_grade})
- Culture: {culture_score}
- Architecture: {architecture_score}
- Integration: {integration_score}
- Talent: {talent_score}

GSTI (Trust Index): {gsti_score}
- Trust Level: {trust_level}
- Deployment Risk: {deployment_risk}

RAI (Return on AI): {rai_ratio}x
RAIA (Return on AI Agents): {raia_ratio}x
RAW (Return on Agentic Workflows): {raw_score}

TOP GAPS: {gaps}
TOP OPPORTUNITIES: {opportunities}

Write a 3-paragraph executive narrative that:
1. Frames the organization's current AI readiness position
2. Identifies the critical inflection points and risks
3. Presents the strategic path forward with specific, actionable recommendations

Tone: Board-level, confident, data-driven. No fluff. Every sentence must deliver value."""

RECOMMENDATION_PROMPT = """Based on the following assessment results, generate structured recommendations.

ASSESSMENT DATA:
{assessment_json}

Generate recommendations in three time horizons:

IMMEDIATE (0-30 days):
- Quick wins that build momentum
- Risk mitigations for critical gaps
- Foundation-setting activities

MID-TERM (30-90 days):
- Capability building initiatives
- Integration improvements
- Talent development programs

STRATEGIC (90+ days):
- Transformation initiatives
- Architecture evolution
- Organizational change programs

For each recommendation include:
- Action title
- Description
- Expected impact on CAITO score
- Required investment level (low/medium/high)
- Dependencies
- Success metrics

Return as structured JSON."""

AGENT_DEPLOYMENT_PROMPT = """Based on the assessment results, create an agent deployment plan.

ASSESSMENT:
{assessment_json}

INDUSTRY: {industry}
INDUSTRY WORKFLOWS: {workflows}

For each recommended workflow automation:
1. Workflow name and description
2. Agent types needed
3. Expected RAIA score
4. Expected RAW contribution
5. Required infrastructure
6. Talent implications
7. Risk factors
8. Implementation timeline
9. Priority score (1-10)

Order by priority. Return as structured JSON."""
