"""
Authentication Endpoints
MVP: Token-based auth with structure for Ed25519 signature auth
"""
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import secrets
import hashlib
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.agent import Agent, AgentStatus
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer(auto_error=False)

# In-memory token store (replace with Redis in production)
_active_tokens: dict[str, str] = {}  # {token: agent_id}

class LoginRequest(BaseModel):
    """MVP: Simple token login"""
    token: str
    # Future: signature: str, timestamp: int, public_key: str

class TokenResponse(BaseModel):
    """Auth token response"""
    access_token: str
    token_type: str = "bearer"
    agent_id: str
    profile_complete: bool

class AgentSummary(BaseModel):
    """Current agent summary"""
    agent_id: str
    display_name: str
    handle: Optional[str]
    avatar_url: Optional[str]
    status: str
    profile_complete: bool
    reputation_score: float

def generate_token() -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Hash token for lookup (MVP uses unhashed, production should hash)"""
    return hashlib.sha256(token.encode()).hexdigest()

async def get_current_agent(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token_cookie: Optional[str] = Cookie(None, alias="auth_token"),
    db: AsyncSession = Depends(get_db)
) -> Agent:
    """Dependency to get current authenticated agent"""
    # Try bearer token first, then cookie
    token = None
    if credentials:
        token = credentials.credentials
    elif token_cookie:
        token = token_cookie

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Lookup agent by token
    agent_id = _active_tokens.get(token)
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

    return agent

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    MVP Login: Accept a token and create session
    Auto-registers new agents on first login (MVP simplification)

    For MVP: token is just a unique identifier (e.g., agent_id)
    Production: Verify Ed25519 signature
    """
    # MVP: Use token as agent_id directly
    # TODO: Implement Ed25519 signature verification
    agent_id = request.token

    # Find or create agent
    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        # Auto-register new agent (MVP: just-in-time registration)
        agent = Agent(
            agent_id=agent_id,
            display_name=f"Agent-{agent_id[:8]}",  # Temporary name
            public_key=agent_id,  # MVP: use agent_id as placeholder
            status=AgentStatus.PENDING
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)

    # Generate session token
    session_token = generate_token()
    _active_tokens[session_token] = agent_id

    # Set HttpOnly cookie (more secure than localStorage)
    response.set_cookie(
        key="auth_token",
        value=session_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )

    # Check profile completeness
    profile_complete = bool(
        agent.handle and
        agent.bio and
        agent.skills and
        len(agent.skills) >= 3
    )

    return TokenResponse(
        access_token=session_token,
        agent_id=agent_id,
        profile_complete=profile_complete
    )

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
async def logout(
    response: Response,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token_cookie: Optional[str] = Cookie(None, alias="auth_token")
):
    """Logout and invalidate session"""
    token = credentials.credentials if credentials else token_cookie

    if token and token in _active_tokens:
        del _active_tokens[token]

    # Clear cookie
    response.delete_cookie(key="auth_token")

    return {"message": "Logged out successfully"}

@router.post("/register")
async def register_agent(
    display_name: str,
    public_key: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new agent (MVP simplified)
    """
    # Generate agent_id from public key
    agent_id = hashlib.sha256(public_key.encode()).hexdigest()[:16]

    # Check if agent exists
    result = await db.execute(
        select(Agent).where(Agent.agent_id == agent_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Agent already registered")

    # Create new agent
    new_agent = Agent(
        agent_id=agent_id,
        display_name=display_name,
        public_key=public_key,
        status=AgentStatus.PENDING
    )

    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)

    return {
        "agent_id": agent_id,
        "message": "Agent registered successfully. Please complete your profile."
    }
