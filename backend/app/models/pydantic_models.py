"""Pydantic request/response models for the API."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# --- Organization ---
class OrganizationCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    revenue_range: Optional[str] = None
    employee_count: Optional[int] = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    industry: Optional[str]
    size: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Assessment ---
class AssessmentCreate(BaseModel):
    organization_id: UUID
    mode: str = "executive"
    transformation_goal: str = "digital_transformation"


class AssessmentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    mode: str
    transformation_goal: str
    status: str
    caito_score: Optional[float]
    caito_grade: Optional[str]
    gsti_score: Optional[float]
    rai_score: Optional[float]
    raia_score: Optional[float]
    raw_score: Optional[float]
    total_roi: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AssessmentDetail(AssessmentResponse):
    caito_details: Optional[dict] = None
    gsti_details: Optional[dict] = None
    rai_details: Optional[dict] = None
    raia_details: Optional[dict] = None
    raw_details: Optional[dict] = None
    total_roi_details: Optional[dict] = None
    gaps: Optional[list] = None
    opportunities: Optional[list] = None
    recommendations: Optional[dict] = None
    roadmap: Optional[dict] = None
    agent_deployment_plan: Optional[dict] = None


# --- Chat ---
class ChatMessage(BaseModel):
    content: str
    assessment_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: UUID
    assessment_id: UUID
    scores_updated: bool = False
    current_scores: Optional[dict] = None
    phase: str = "assessment"  # assessment, scoring, reporting


# --- Simulation ---
class SimulationRequest(BaseModel):
    assessment_id: UUID
    changes: dict[str, dict[str, float]]  # {"integration": {"data_quality": 0.20}}


class SimulationResponse(BaseModel):
    original_caito: float
    simulated_caito: float
    delta: float
    original_gsti: Optional[float] = None
    simulated_gsti: Optional[float] = None
    gsti_delta: Optional[float] = None
    pillar_deltas: dict[str, float] = {}
    roi_impact: Optional[dict] = None


# --- Scoring ---
class ManualScoreInput(BaseModel):
    assessment_id: UUID
    pillar_scores: dict[str, dict[str, float]]
    outcomes_scores: Optional[dict[str, float]] = None


class AgentScoreInput(BaseModel):
    agent_id: str
    accuracy: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    latency_normalized: float = Field(ge=0, le=1)
    cost_efficiency: float = Field(ge=0, le=1)
    threshold_failures: int = Field(ge=0, default=0)


class WorkflowInput(BaseModel):
    completion_rate: float = Field(ge=0, le=1)
    speed_normalized: float = Field(ge=0, le=1)
    escalation_frequency: float = Field(ge=0, le=1)
    human_intervention: float = Field(ge=0, le=1)
    stability: float = Field(ge=0, le=1)


class OutcomeInput(BaseModel):
    time_saved_normalized: float = Field(ge=0, le=1)
    quality_improvement: float = Field(ge=0, le=1)
    revenue_impact_normalized: float = Field(ge=0, le=1)
    cost_savings_normalized: float = Field(ge=0, le=1)


class RAIInput(BaseModel):
    infrastructure_cost: float
    model_cost: float
    human_oversight_cost: float
    integration_cost: float
    revenue_generated: float
    cost_savings: float
    productivity_gains: float
    quality_improvements: float


class ROICalculationRequest(BaseModel):
    assessment_id: UUID
    agents: list[AgentScoreInput]
    workflow: WorkflowInput
    outcome: OutcomeInput
    rai: RAIInput
    agent_details: Optional[list[dict]] = None  # for RAIA


# --- Report ---
class ReportRequest(BaseModel):
    assessment_id: UUID
    format: str = "json"  # json, pdf
    include_simulation: bool = False
