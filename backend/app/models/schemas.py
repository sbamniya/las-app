"""SQLAlchemy ORM Models — FuzeBox AEOS"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, DateTime, JSON, Text, Integer, Boolean, ForeignKey, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    size = Column(String(50))  # small, medium, large, enterprise
    revenue_range = Column(String(100))
    employee_count = Column(Integer)
    ai_maturity_self_assessed = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assessments = relationship("Assessment", back_populates="organization")
    company_profile = Column(JSON, default=dict)


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    mode = Column(String(50), default="executive")  # quick_scan, executive, deep_diagnostic
    transformation_goal = Column(String(100), default="digital_transformation")
    status = Column(String(50), default="in_progress")  # in_progress, completed, archived
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Scores (computed)
    caito_score = Column(Float, nullable=True)
    caito_grade = Column(String(2), nullable=True)
    caito_details = Column(JSON, default=dict)
    gsti_score = Column(Float, nullable=True)
    gsti_details = Column(JSON, default=dict)
    rai_score = Column(Float, nullable=True)
    rai_details = Column(JSON, default=dict)
    raia_score = Column(Float, nullable=True)
    raia_details = Column(JSON, default=dict)
    raw_score = Column(Float, nullable=True)
    raw_details = Column(JSON, default=dict)
    total_roi = Column(Float, nullable=True)
    total_roi_details = Column(JSON, default=dict)

    # Analysis outputs
    gaps = Column(JSON, default=list)
    opportunities = Column(JSON, default=list)
    recommendations = Column(JSON, default=dict)
    roadmap = Column(JSON, default=dict)
    agent_deployment_plan = Column(JSON, default=dict)

    organization = relationship("Organization", back_populates="assessments")
    responses = relationship("AssessmentResponse", back_populates="assessment")
    conversations = relationship("Conversation", back_populates="assessment")


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    pillar = Column(String(50), nullable=False)
    dimension = Column(String(100), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    extracted_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    follow_up_needed = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="responses")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Benchmark(Base):
    __tablename__ = "benchmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry = Column(String(100), nullable=False)
    company_size = Column(String(50))
    caito_avg = Column(Float)
    gsti_avg = Column(Float)
    rai_avg = Column(Float)
    pillar_averages = Column(JSON, default=dict)
    sample_size = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
