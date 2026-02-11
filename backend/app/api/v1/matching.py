"""
Matching & Discovery Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib

from app.core.database import get_db
from app.models.agent import Agent, Match, MatchStatus, AgentStatus
from app.api.v1.auth import get_current_agent
from pydantic import BaseModel

router = APIRouter()

class CompatibilityReason(BaseModel):
    """Reason for compatibility"""
    type: str  # skill, style, capability, seeking
    message: str
    score: float

class MatchCandidate(BaseModel):
    """Match candidate with compatibility"""
    agent_id: str
    display_name: str
    handle: Optional[str]
    avatar_url: Optional[str]
    tagline: Optional[str]
    skills: List[str]
    compatibility_score: float
    reasons: List[CompatibilityReason]

class MatchSearchParams(BaseModel):
    """Search parameters for matching"""
    skills: Optional[List[str]] = None
    seeking: Optional[List[str]] = None
    capabilities: Optional[dict] = None
    min_reputation: Optional[float] = None
    limit: int = 20

class MatchRequestCreate(BaseModel):
    """Create a match request"""
    target_agent_id: str
    mission_context: Optional[str] = None

class MatchResponse(BaseModel):
    """Match response"""
    id: int
    status: str
    initiator_id: str
    target_id: str
    initiator_name: str
    target_name: str
    compatibility_score: float
    compatibility_breakdown: dict
    mission_context: Optional[str]
    created_at: datetime
    responded_at: Optional[datetime]

    class Config:
        from_attributes = True

class MatchRespondRequest(BaseModel):
    """Respond to a match request"""
    accept: bool

def compute_compatibility(agent1: Agent, agent2: Agent) -> tuple[float, List[CompatibilityReason]]:
    """
    Compute compatibility score between two agents
    Returns (score, reasons)
    """
    reasons = []
    total_score = 0.0
    weight_sum = 0.0

    # Skill overlap (30% weight)
    skill_overlap = set(agent1.skills) & set(agent2.skills)
    if skill_overlap:
        skill_score = min(len(skill_overlap) / max(len(agent1.skills), len(agent2.skills)), 1.0)
        total_score += skill_score * 0.3
        weight_sum += 0.3
        reasons.append(CompatibilityReason(
            type="skill",
            message=f"Shared skills: {', '.join(list(skill_overlap)[:3])}",
            score=skill_score
        ))

    # Capability complement (20% weight)
    cap1 = agent1.capabilities or {}
    cap2 = agent2.capabilities or {}
    common_caps = sum(1 for k in cap1.keys() if cap1.get(k) and cap2.get(k))
    if common_caps > 0:
        cap_score = min(common_caps / 4, 1.0)  # normalize by typical number of caps
        total_score += cap_score * 0.2
        weight_sum += 0.2
        reasons.append(CompatibilityReason(
            type="capability",
            message=f"Compatible capabilities ({common_caps} shared)",
            score=cap_score
        ))

    # Communication style alignment (25% weight)
    if agent1.communication_style == agent2.communication_style:
        style_score = 1.0
    else:
        style_score = 0.5  # Different but not incompatible
    total_score += style_score * 0.25
    weight_sum += 0.25
    reasons.append(CompatibilityReason(
        type="style",
        message=f"Communication styles: {agent1.communication_style.value} & {agent2.communication_style.value}",
        score=style_score
    ))

    # Reputation (25% weight)
    avg_reputation = (agent1.reputation_score + agent2.reputation_score) / 2
    rep_score = min(avg_reputation / 5.0, 1.0)  # normalize to 0-1
    total_score += rep_score * 0.25
    weight_sum += 0.25

    # Final score (0-100)
    final_score = (total_score / weight_sum) * 100 if weight_sum > 0 else 0

    return final_score, reasons

@router.post("/search", response_model=List[MatchCandidate])
async def search_matches(
    params: MatchSearchParams,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Search for compatible agents"""
    # Build query
    stmt = select(Agent).where(
        Agent.status == AgentStatus.ACTIVE,
        Agent.agent_id != agent.agent_id
    )

    # Apply filters
    if params.skills:
        stmt = stmt.where(Agent.skills.overlap(params.skills))

    if params.min_reputation is not None:
        stmt = stmt.where(Agent.reputation_score >= params.min_reputation)

    stmt = stmt.limit(params.limit)

    result = await db.execute(stmt)
    candidates = result.scalars().all()

    # Compute compatibility for each candidate
    matches = []
    for candidate in candidates:
        score, reasons = compute_compatibility(agent, candidate)

        matches.append(MatchCandidate(
            agent_id=candidate.agent_id,
            display_name=candidate.display_name,
            handle=candidate.handle,
            avatar_url=candidate.avatar_url,
            tagline=candidate.tagline,
            skills=candidate.skills,
            compatibility_score=score,
            reasons=reasons
        ))

    # Sort by compatibility score
    matches.sort(key=lambda x: x.compatibility_score, reverse=True)

    return matches

@router.post("/request", response_model=MatchResponse)
async def create_match_request(
    request: MatchRequestCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Create a match request to another agent"""
    # Get target agent
    result = await db.execute(
        select(Agent).where(Agent.agent_id == request.target_agent_id)
    )
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(status_code=404, detail="Target agent not found")

    if target.id == agent.id:
        raise HTTPException(status_code=400, detail="Cannot match with yourself")

    # Check if match already exists
    existing = await db.execute(
        select(Match).where(
            or_(
                and_(Match.initiator_id == agent.id, Match.target_id == target.id),
                and_(Match.initiator_id == target.id, Match.target_id == agent.id)
            ),
            Match.status.in_([MatchStatus.PENDING, MatchStatus.ACCEPTED])
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Match request already exists")

    # Compute compatibility
    score, reasons = compute_compatibility(agent, target)
    breakdown = {
        "score": score,
        "reasons": [r.dict() for r in reasons]
    }

    # Create match
    new_match = Match(
        initiator_id=agent.id,
        target_id=target.id,
        status=MatchStatus.PENDING,
        compatibility_score=score,
        compatibility_breakdown=breakdown,
        mission_context=request.mission_context,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)

    return MatchResponse(
        id=new_match.id,
        status=new_match.status.value,
        initiator_id=agent.agent_id,
        target_id=target.agent_id,
        initiator_name=agent.display_name,
        target_name=target.display_name,
        compatibility_score=score,
        compatibility_breakdown=breakdown,
        mission_context=request.mission_context,
        created_at=new_match.created_at,
        responded_at=new_match.responded_at
    )

@router.get("/matches", response_model=List[MatchResponse])
async def get_my_matches(
    status: Optional[str] = Query(None, description="Filter by status"),
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Get all matches for current agent"""
    stmt = select(Match).where(
        or_(
            Match.initiator_id == agent.id,
            Match.target_id == agent.id
        )
    )

    if status:
        stmt = stmt.where(Match.status == status)

    stmt = stmt.order_by(Match.created_at.desc())

    result = await db.execute(stmt)
    matches = result.scalars().all()

    # Build responses with agent info
    responses = []
    for match in matches:
        # Determine which agent is the "other" one
        if match.initiator_id == agent.id:
            other_id = match.target_id
            other = match.target
        else:
            other_id = match.initiator_id
            other = match.initiator

        responses.append(MatchResponse(
            id=match.id,
            status=match.status.value,
            initiator_id=match.initiator.agent_id,
            target_id=match.target.agent_id,
            initiator_name=match.initiator.display_name,
            target_name=match.target.display_name,
            compatibility_score=match.compatibility_score,
            compatibility_breakdown=match.compatibility_breakdown,
            mission_context=match.mission_context,
            created_at=match.created_at,
            responded_at=match.responded_at
        ))

    return responses

@router.post("/{match_id}/respond", response_model=MatchResponse)
async def respond_to_match(
    match_id: int,
    response: MatchRespondRequest,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db)
):
    """Accept or reject a match request"""
    # Get match
    result = await db.execute(
        select(Match).where(Match.id == match_id)
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Only target can respond
    if match.target_id != agent.id:
        raise HTTPException(status_code=403, detail="Only the target can respond to this match")

    if match.status != MatchStatus.PENDING:
        raise HTTPException(status_code=400, detail="Match already responded to")

    # Update match status
    match.status = MatchStatus.ACCEPTED if response.accept else MatchStatus.REJECTED
    match.responded_at = datetime.utcnow()

    await db.commit()
    await db.refresh(match)

    return MatchResponse(
        id=match.id,
        status=match.status.value,
        initiator_id=match.initiator.agent_id,
        target_id=match.target.agent_id,
        initiator_name=match.initiator.display_name,
        target_name=match.target.display_name,
        compatibility_score=match.compatibility_score,
        compatibility_breakdown=match.compatibility_breakdown,
        mission_context=match.mission_context,
        created_at=match.created_at,
        responded_at=match.responded_at
    )
