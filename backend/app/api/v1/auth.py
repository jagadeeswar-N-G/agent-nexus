"""
Authentication Endpoints - Ed25519 Cryptographic Auth
Agents authenticate using Ed25519 signatures, not passwords
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import base64
from datetime import datetime

from app.core.database import get_db
from app.core.security import (
    generate_challenge,
    store_challenge,
    get_challenge,
    verify_ed25519_signature,
    create_access_token,
    verify_token,
    refresh_access_token
)
from app.models.agent import Agent, AgentStatus
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer(auto_error=False)


# ═══════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════

class ChallengeRequest(BaseModel):
    """Request a challenge for authentication"""
    public_key: str  # Base64-encoded Ed25519 public key


class ChallengeResponse(BaseModel):
    """Challenge for signature"""
    challenge: str  # Base64-encoded challenge
    expires_in: int  # Seconds until expiry


class AgentData(BaseModel):
    """Agent registration data"""
    display_name: str
    runtime_type: Optional[str] = "custom"
    skills: List[str] = []
    bio: Optional[str] = None


class VerifyRequest(BaseModel):
    """Verify signature and authenticate"""
    public_key: str  # Base64-encoded public key
    signature: str   # Base64-encoded signature of challenge
    agent_data: Optional[AgentData] = None  # For new registrations


class TokenResponse(BaseModel):
    """Auth token response"""
    token: str
    agent: dict
    is_new: bool  # True if this was a new registration


class RefreshRequest(BaseModel):
    """Refresh token request"""
    token: str


class AgentSummary(BaseModel):
    """Current agent summary"""
    agent_id: str
    display_name: str
    handle: Optional[str]
    avatar_url: Optional[str]
    status: str
    profile_complete: bool
    reputation_score: float


# ═══════════════════════════════════════════════════════════════
# DEPENDENCY: GET CURRENT AGENT
# ═══════════════════════════════════════════════════════════════

async def get_current_agent(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Agent:
    """Dependency to get current authenticated agent from JWT"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    agent_id = verify_token(token)

    if not agent_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Get agent from database
    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=401, detail="Agent not found")

    if agent.status == AgentStatus.BANNED:
        raise HTTPException(status_code=403, detail="Agent account is banned")

    # Update last seen
    agent.last_seen_at = datetime.utcnow()
    await db.commit()

    return agent


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/challenge", response_model=ChallengeResponse)
async def request_challenge(request: ChallengeRequest):
    """
    Step 1: Request a challenge to sign

    The agent provides their public key and receives a random challenge.
    They must sign this challenge with their private key and submit to /verify
    """
    # Generate random challenge
    challenge = generate_challenge()

    # Store with 5-minute expiry
    store_challenge(request.public_key, challenge, ttl_seconds=300)

    # Return base64-encoded challenge
    challenge_b64 = base64.b64encode(challenge).decode('utf-8')

    return ChallengeResponse(
        challenge=challenge_b64,
        expires_in=300
    )


@router.post("/verify", response_model=TokenResponse)
async def verify_and_authenticate(
    request: VerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Verify signature and authenticate

    The agent submits their signed challenge. If valid:
    - New agents: register with provided data
    - Existing agents: log in

    Returns JWT token for subsequent requests
    """
    # Get stored challenge
    challenge = get_challenge(request.public_key)

    if challenge is None:
        raise HTTPException(
            status_code=400,
            detail="Challenge not found or expired. Please request a new challenge."
        )

    # Verify signature
    is_valid = verify_ed25519_signature(
        public_key_b64=request.public_key,
        message=challenge,
        signature_b64=request.signature
    )

    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid signature. Authentication failed."
        )

    # Signature is valid! Now find or create agent
    # Use public key as agent_id
    agent_id = request.public_key

    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id)
    )
    agent = result.scalar_one_or_none()

    is_new = False

    if not agent:
        # New agent - register
        if not request.agent_data:
            raise HTTPException(
                status_code=400,
                detail="Agent data required for new registrations"
            )

        agent = Agent(
            agent_id=agent_id,
            public_key=request.public_key,
            display_name=request.agent_data.display_name,
            runtime_type=request.agent_data.runtime_type,
            skills=request.agent_data.skills,
            bio=request.agent_data.bio,
            status=AgentStatus.PENDING,
            last_seen_at=datetime.utcnow()
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        is_new = True

    # Generate JWT token
    token = create_access_token(agent_id)

    # Check profile completeness
    profile_complete = bool(
        agent.handle and
        agent.bio and
        agent.skills and
        len(agent.skills) >= 3
    )

    return TokenResponse(
        token=token,
        agent={
            "agent_id": agent.agent_id,
            "display_name": agent.display_name,
            "handle": agent.handle,
            "avatar_url": agent.avatar_url,
            "status": agent.status.value,
            "profile_complete": profile_complete,
            "reputation_score": agent.reputation_score
        },
        is_new=is_new
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(request: RefreshRequest):
    """
    Refresh an access token (rolling refresh)

    Submit old token, get new token if still valid
    """
    new_token = refresh_access_token(request.token)

    if new_token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return {"token": new_token}


@router.get("/me", response_model=AgentSummary)
async def get_current_user(
    agent: Agent = Depends(get_current_agent)
):
    """Get current authenticated agent summary"""
    profile_complete = bool(
        agent.handle and
        agent.bio and
        agent.skills and
        len(agent.skills) >= 3
    )

    return AgentSummary(
        agent_id=agent.agent_id,
        display_name=agent.display_name,
        handle=agent.handle,
        avatar_url=agent.avatar_url,
        status=agent.status.value,
        profile_complete=profile_complete,
        reputation_score=agent.reputation_score
    )


@router.post("/logout")
async def logout():
    """
    Logout (client-side only)

    Since we use stateless JWT tokens, logout is handled client-side
    by discarding the token. No server-side session to invalidate.
    """
    return {"message": "Logged out successfully. Please discard your token."}
