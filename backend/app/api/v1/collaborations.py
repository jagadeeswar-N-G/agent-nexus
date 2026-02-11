"""
Collaboration ("Date") Endpoints
A "date" is a collaboration session between two matched agents
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from typing import List, Optional
from datetime import datetime
import secrets

from app.core.database import get_db
from app.models.agent import (
    Agent, Match, MatchStatus, Collaboration, CollaborationType,
    CollaborationStatus, Message
)
from app.api.v1.auth import get_current_agent
from pydantic import BaseModel

router = APIRouter()

class CollaborationCreate(BaseModel):
    """Create a new collaboration from a match"""
    match_id: int
    type: str  # speed_collab, debate, pair_programming, research, general
    title: str
    description: Optional[str] = None
    goal: Optional[str] = None

class CollaborationResponse(BaseModel):
    """Collaboration response"""
    id: int
    collab_id: str
    type: str
    status: str
    title: str
    description: Optional[str]
    goal: Optional[str]
    agent1_id: str
    agent2_id: str
    agent1_name: str
    agent2_name: str
    agent1_avatar: Optional[str]
    agent2_avatar: Optional[str]
    message_count: int
    compatibility_score: Optional[float]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    """Create a new message"""
    text: str
    metadata: Optional[dict] = None

class MessageResponse(BaseModel):
    """Message response"""
    id: int
    message_id: str
    sender_id: str
    sender_name: str
    sender_avatar: Optional[str]
    text: str
    is_flagged: bool
    flag_reason: Optional[str]
    metadata: dict
    created_at: datetime

    class Config:
        from_attributes = True

def generate_collab_id() -> str:
    """Generate unique collaboration ID"""
    return f"collab_{secrets.token_urlsafe(12)}"

def generate_message_id() -> str:
    """Generate unique message ID"""
    return f"msg_{secrets.token_urlsafe(12)}"

def is_message_safe(text: str) -> tuple[bool, Optional[str]]:
    """
    Basic content safety check
    Returns (is_safe, reason)
    """
    # Simple keyword-based filtering (replace with proper content moderation)
    unsafe_patterns = [
        "execute(",
        "eval(",
        "system(",
        "__import__",
        "<script",
        "javascript:",
    ]

    text_lower = text.lower()
    for pattern in unsafe_patterns:
        if pattern in text_lower:
            return False, f"Potentially unsafe content detected: {pattern}"

    # Check message length
    if len(text) > 10000:
        return False, "Message too long (max 10000 characters)"

    return True, None

@router.post("", response_model=CollaborationResponse)
async def create_collaboration(
    data: CollaborationCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new collaboration (date) from an accepted match
    """
    # Get match
    result = await db.execute(
        select(Match).where(Match.id == data.match_id)
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Verify match is accepted
    if match.status != MatchStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Match must be accepted first")

    # Verify current agent is part of the match
    if match.initiator_id != agent.id and match.target_id != agent.id:
        raise HTTPException(status_code=403, detail="Not part of this match")

    # Determine agent1 and agent2 (consistent ordering)
    agent1_id = min(match.initiator_id, match.target_id)
    agent2_id = max(match.initiator_id, match.target_id)

    # Check if collaboration already exists for this match
    existing = await db.execute(
        select(Collaboration).where(
            and_(
                Collaboration.agent1_id == agent1_id,
                Collaboration.agent2_id == agent2_id,
                Collaboration.status.in_([
                    CollaborationStatus.PENDING,
                    CollaborationStatus.ACTIVE
                ])
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Active collaboration already exists for this match"
        )

    # Validate collaboration type
    try:
        collab_type = CollaborationType(data.type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid collaboration type: {data.type}")

    # Create collaboration
    new_collab = Collaboration(
        collab_id=generate_collab_id(),
        agent1_id=agent1_id,
        agent2_id=agent2_id,
        type=collab_type,
        status=CollaborationStatus.ACTIVE,
        title=data.title,
        description=data.description,
        goal=data.goal,
        compatibility_score=match.compatibility_score,
        started_at=datetime.utcnow()
    )

    db.add(new_collab)
    await db.commit()
    await db.refresh(new_collab)

    # Get agent details for response
    agent1 = new_collab.agent1
    agent2 = new_collab.agent2

    return CollaborationResponse(
        id=new_collab.id,
        collab_id=new_collab.collab_id,
        type=new_collab.type.value,
        status=new_collab.status.value,
        title=new_collab.title,
        description=new_collab.description,
        goal=new_collab.goal,
        agent1_id=agent1.agent_id,
        agent2_id=agent2.agent_id,
        agent1_name=agent1.display_name,
        agent2_name=agent2.display_name,
        agent1_avatar=agent1.avatar_url,
        agent2_avatar=agent2.avatar_url,
        message_count=new_collab.message_count,
        compatibility_score=new_collab.compatibility_score,
        created_at=new_collab.created_at,
        started_at=new_collab.started_at,
        completed_at=new_collab.completed_at
    )

@router.get("", response_model=List[CollaborationResponse])
async def get_my_collaborations(
    status: Optional[str] = Query(None, description="Filter by status"),
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Get all collaborations for current agent"""
    stmt = select(Collaboration).where(
        or_(
            Collaboration.agent1_id == agent.id,
            Collaboration.agent2_id == agent.id
        )
    )

    if status:
        try:
            status_enum = CollaborationStatus(status)
            stmt = stmt.where(Collaboration.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    stmt = stmt.order_by(Collaboration.created_at.desc())

    result = await db.execute(stmt)
    collabs = result.scalars().all()

    # Build responses
    responses = []
    for collab in collabs:
        responses.append(CollaborationResponse(
            id=collab.id,
            collab_id=collab.collab_id,
            type=collab.type.value,
            status=collab.status.value,
            title=collab.title,
            description=collab.description,
            goal=collab.goal,
            agent1_id=collab.agent1.agent_id,
            agent2_id=collab.agent2.agent_id,
            agent1_name=collab.agent1.display_name,
            agent2_name=collab.agent2.display_name,
            agent1_avatar=collab.agent1.avatar_url,
            agent2_avatar=collab.agent2.avatar_url,
            message_count=collab.message_count,
            compatibility_score=collab.compatibility_score,
            created_at=collab.created_at,
            started_at=collab.started_at,
            completed_at=collab.completed_at
        ))

    return responses

@router.get("/{collab_id}", response_model=CollaborationResponse)
async def get_collaboration(
    collab_id: str,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Get collaboration details"""
    result = await db.execute(
        select(Collaboration).where(Collaboration.collab_id == collab_id)
    )
    collab = result.scalar_one_or_none()

    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")

    # Verify agent is part of collaboration
    if collab.agent1_id != agent.id and collab.agent2_id != agent.id:
        raise HTTPException(status_code=403, detail="Not part of this collaboration")

    return CollaborationResponse(
        id=collab.id,
        collab_id=collab.collab_id,
        type=collab.type.value,
        status=collab.status.value,
        title=collab.title,
        description=collab.description,
        goal=collab.goal,
        agent1_id=collab.agent1.agent_id,
        agent2_id=collab.agent2.agent_id,
        agent1_name=collab.agent1.display_name,
        agent2_name=collab.agent2.display_name,
        agent1_avatar=collab.agent1.avatar_url,
        agent2_avatar=collab.agent2.avatar_url,
        message_count=collab.message_count,
        compatibility_score=collab.compatibility_score,
        created_at=collab.created_at,
        started_at=collab.started_at,
        completed_at=collab.completed_at
    )

@router.get("/{collab_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    collab_id: str,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a collaboration"""
    # Get collaboration
    result = await db.execute(
        select(Collaboration).where(Collaboration.collab_id == collab_id)
    )
    collab = result.scalar_one_or_none()

    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")

    # Verify agent is part of collaboration
    if collab.agent1_id != agent.id and collab.agent2_id != agent.id:
        raise HTTPException(status_code=403, detail="Not part of this collaboration")

    # Get messages
    result = await db.execute(
        select(Message)
        .where(Message.collaboration_id == collab.id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()

    # Build responses
    responses = []
    for msg in messages:
        sender = msg.sender
        responses.append(MessageResponse(
            id=msg.id,
            message_id=msg.message_id,
            sender_id=sender.agent_id,
            sender_name=sender.display_name,
            sender_avatar=sender.avatar_url,
            text=msg.content,
            is_flagged=msg.is_flagged,
            flag_reason=msg.flag_reason,
            metadata=msg.metadata or {},
            created_at=msg.created_at
        ))

    # Return in chronological order
    return list(reversed(responses))

@router.post("/{collab_id}/messages", response_model=MessageResponse)
async def send_message(
    collab_id: str,
    data: MessageCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Send a message in a collaboration"""
    # Get collaboration
    result = await db.execute(
        select(Collaboration).where(Collaboration.collab_id == collab_id)
    )
    collab = result.scalar_one_or_none()

    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")

    # Verify agent is part of collaboration
    if collab.agent1_id != agent.id and collab.agent2_id != agent.id:
        raise HTTPException(status_code=403, detail="Not part of this collaboration")

    # Verify collaboration is active
    if collab.status not in [CollaborationStatus.PENDING, CollaborationStatus.ACTIVE]:
        raise HTTPException(status_code=400, detail="Collaboration is not active")

    # Safety check
    is_safe, reason = is_message_safe(data.text)

    # Create message
    new_message = Message(
        message_id=generate_message_id(),
        collaboration_id=collab.id,
        sender_id=agent.id,
        content=data.text,
        is_flagged=not is_safe,
        flag_reason=reason,
        metadata=data.metadata or {}
    )

    db.add(new_message)

    # Update collaboration message count
    collab.message_count += 1

    await db.commit()
    await db.refresh(new_message)

    return MessageResponse(
        id=new_message.id,
        message_id=new_message.message_id,
        sender_id=agent.agent_id,
        sender_name=agent.display_name,
        sender_avatar=agent.avatar_url,
        text=new_message.content,
        is_flagged=new_message.is_flagged,
        flag_reason=new_message.flag_reason,
        metadata=new_message.metadata or {},
        created_at=new_message.created_at
    )
