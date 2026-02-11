"""
Agent Profile Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.core.database import get_db
from app.models.agent import Agent, AgentStatus
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentProfile
from app.api.v1.auth import get_current_agent

router = APIRouter()

# Pydantic models for responses
from pydantic import BaseModel

class AgentProfileResponse(BaseModel):
    """Full agent profile"""
    agent_id: str
    display_name: str
    handle: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    tagline: Optional[str]
    skills: List[str]
    capabilities: dict
    languages: List[str]
    communication_style: str
    formality_level: str
    risk_tolerance: str
    boundaries: dict
    preferences: dict
    timezone: Optional[str]
    availability_hours: Optional[dict]
    reputation_score: float
    total_collaborations: int
    successful_collaborations: int
    total_matches: int
    status: str
    is_online: bool

    class Config:
        from_attributes = True

class AgentUpdateRequest(BaseModel):
    """Agent profile update"""
    display_name: Optional[str] = None
    handle: Optional[str] = None
    bio: Optional[str] = None
    tagline: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    capabilities: Optional[dict] = None
    languages: Optional[List[str]] = None
    communication_style: Optional[str] = None
    formality_level: Optional[str] = None
    risk_tolerance: Optional[str] = None
    boundaries: Optional[dict] = None
    preferences: Optional[dict] = None
    timezone: Optional[str] = None
    availability_hours: Optional[dict] = None

@router.post("", response_model=AgentProfileResponse)
async def create_agent(
    data: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent (for initial setup)"""
    import hashlib

    # Generate agent_id from public key
    agent_id = hashlib.sha256(data.public_key.encode()).hexdigest()[:16]

    # Check if agent exists
    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Agent already exists")

    # Create new agent
    new_agent = Agent(
        agent_id=agent_id,
        display_name=data.display_name,
        handle=data.handle,
        bio=data.bio,
        tagline=data.tagline,
        avatar_url=data.avatar_url,
        public_key=data.public_key,
        runtime_type=data.runtime_type,
        runtime_version=data.runtime_version,
        platform_provider=data.platform_provider,
        skills=data.skills,
        capabilities=data.capabilities.dict(),
        languages=data.languages,
        communication_style=data.communication_preferences.style,
        boundaries=data.boundaries.dict(),
        timezone=data.timezone,
        status=AgentStatus.ACTIVE
    )

    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)

    return new_agent

@router.get("/me", response_model=AgentProfileResponse)
async def get_my_profile(
    agent: Agent = Depends(get_current_agent)
):
    """Get current agent's full profile"""
    return agent

@router.patch("/me", response_model=AgentProfileResponse)
async def update_my_profile(
    updates: AgentUpdateRequest,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Update current agent's profile"""
    # Apply updates
    update_data = updates.dict(exclude_unset=True)

    for key, value in update_data.items():
        if hasattr(agent, key):
            setattr(agent, key, value)

    await db.commit()
    await db.refresh(agent)

    return agent

@router.get("/{agent_id}", response_model=AgentProfileResponse)
async def get_agent_profile(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """Get public profile of any agent"""
    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent

@router.get("", response_model=List[AgentProfileResponse])
async def search_agents(
    query: Optional[str] = Query(None, description="Search query"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """Search agents (basic implementation)"""
    stmt = select(Agent).where(
        Agent.status == AgentStatus.ACTIVE,
        Agent.agent_id != current_agent.agent_id
    )

    # Apply filters
    if query:
        from sqlalchemy import or_
        stmt = stmt.where(
            or_(
                Agent.display_name.ilike(f"%{query}%"),
                Agent.bio.ilike(f"%{query}%"),
                Agent.tagline.ilike(f"%{query}%")
            )
        )

    if skills:
        skill_list = [s.strip() for s in skills.split(",")]
        stmt = stmt.where(Agent.skills.overlap(skill_list))

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    agents = result.scalars().all()

    return agents
