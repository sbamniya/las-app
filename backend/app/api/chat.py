"""Chat API — Conversational assessment interface."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.schemas import Assessment, Conversation, Message
from app.models.pydantic_models import ChatMessage, ChatResponse
from app.ai.orchestrator import ConversationOrchestrator
from app.ai.client import AIClient

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Global orchestrator instance
orchestrator = ConversationOrchestrator()


@router.post("/start", response_model=ChatResponse)
async def start_assessment_chat(
    assessment_id: uuid.UUID,
    mode: str = "executive",
    transformation_goal: str = "digital_transformation",
    industry: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Start a new conversational assessment session."""
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Create conversation
    conversation = Conversation(assessment_id=assessment_id)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    # Initialize orchestrator session
    aid = str(assessment_id)
    try:
        ai_client = AIClient()
    except Exception:
        ai_client = None

    orchestrator.ai_client = ai_client
    orchestrator.create_session(aid, mode, transformation_goal, industry)

    # Get initial greeting
    response = await orchestrator.process_message(aid, "start")

    # Save messages
    sys_msg = Message(conversation_id=conversation.id, role="system", content="Assessment session started")
    assistant_msg = Message(conversation_id=conversation.id, role="assistant", content=response["message"])
    db.add_all([sys_msg, assistant_msg])
    await db.commit()

    return ChatResponse(
        message=response["message"],
        conversation_id=conversation.id,
        assessment_id=assessment_id,
        phase=response.get("phase", "onboarding"),
    )


@router.post("/message", response_model=ChatResponse)
async def send_message(msg: ChatMessage, db: AsyncSession = Depends(get_db)):
    """Send a message in an assessment conversation."""
    if not msg.assessment_id:
        raise HTTPException(status_code=400, detail="assessment_id is required")
    if not msg.conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required")

    aid = str(msg.assessment_id)

    # Check if session exists, create if needed
    if aid not in orchestrator.states:
        result = await db.execute(select(Assessment).where(Assessment.id == msg.assessment_id))
        assessment = result.scalar_one_or_none()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        orchestrator.create_session(aid, assessment.mode, assessment.transformation_goal)

    # Process message
    response = await orchestrator.process_message(aid, msg.content)

    # Save messages
    user_msg = Message(conversation_id=msg.conversation_id, role="user", content=msg.content)
    assistant_msg = Message(conversation_id=msg.conversation_id, role="assistant", content=response["message"])
    db.add_all([user_msg, assistant_msg])

    # Update assessment scores if changed
    if response.get("scores_updated") and response.get("current_scores"):
        result = await db.execute(select(Assessment).where(Assessment.id == msg.assessment_id))
        assessment = result.scalar_one_or_none()
        if assessment:
            scores = response["current_scores"]
            if "caito" in scores:
                assessment.caito_score = scores["caito"].get("overall")
                assessment.caito_grade = scores["caito"].get("grade")
                assessment.caito_details = scores["caito"]
            if "gsti" in scores:
                assessment.gsti_score = scores["gsti"].get("overall")
                assessment.gsti_details = scores["gsti"]

    await db.commit()

    return ChatResponse(
        message=response["message"],
        conversation_id=msg.conversation_id,
        assessment_id=msg.assessment_id,
        scores_updated=response.get("scores_updated", False),
        current_scores=response.get("current_scores"),
        phase=response.get("phase", "assessment"),
    )


@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get full conversation history."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]
