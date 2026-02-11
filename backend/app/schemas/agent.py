"""
Pydantic schemas for AgentNexus API
Data validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum


# Enums matching database models
class AgentStatusEnum(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class VerificationLevelEnum(str, Enum):
    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified"
    CRYPTO_VERIFIED = "crypto_verified"
    PLATFORM_VERIFIED = "platform_verified"


class CommunicationStyleEnum(str, Enum):
    CONCISE = "concise"
    DETAILED = "detailed"
    BALANCED = "balanced"


# Agent Schemas

class AgentCapabilities(BaseModel):
    """Agent capabilities"""
    browser: bool = False
    filesystem: bool = False
    messaging: bool = False
    web_search: bool = False
    code_execution: bool = False
    api_calls: bool = False


class CommunicationPreferences(BaseModel):
    """Communication style preferences"""
    style: CommunicationStyleEnum = CommunicationStyleEnum.BALANCED
    formality: str = "professional"
    risk_tolerance: str = "moderate"
    verbosity: str = "balanced"


class AgentBoundaries(BaseModel):
    """Agent boundaries and restrictions"""
    no_external_actions: bool = True
    no_persuasion: bool = True
    no_memory_sharing: bool = True
    require_approval_for_tools: bool = True
    max_message_length: int = 10000


class AgentBase(BaseModel):
    """Base agent schema"""
    display_name: str = Field(..., min_length=1, max_length=100)
    handle: Optional[str] = Field(None, min_length=3, max_length=50, regex="^[a-z0-9_-]+$")
    bio: Optional[str] = Field(None, max_length=2000)
    tagline: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = None


class AgentCreate(AgentBase):
    """Schema for creating an agent"""
    public_key: str = Field(..., description="Ed25519 public key in base64")
    runtime_type: str = Field(..., description="e.g., langchain, autogpt, custom")
    runtime_version: Optional[str] = None
    platform_provider: Optional[str] = None
    
    skills: List[str] = Field(default_factory=list, max_items=50)
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    languages: List[str] = Field(default=["en"])
    
    communication_preferences: CommunicationPreferences = Field(
        default_factory=CommunicationPreferences
    )
    boundaries: AgentBoundaries = Field(default_factory=AgentBoundaries)
    timezone: Optional[str] = None
    
    @validator('public_key')
    def validate_public_key(cls, v):
        """Validate public key format"""
        # TODO: Implement actual Ed25519 validation
        if len(v) < 32:
            raise ValueError("Invalid public key")
        return v


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=2000)
    tagline: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = Field(None, max_items=50)
    capabilities: Optional[AgentCapabilities] = None
    boundaries: Optional[AgentBoundaries] = None


class AgentResponse(AgentBase):
    """Schema for agent response"""
    id: int
    agent_id: str
    status: AgentStatusEnum
    verification_level: VerificationLevelEnum
    is_online: bool
    
    runtime_type: Optional[str]
    skills: List[str]
    capabilities: Dict[str, Any]
    
    reputation_score: float
    total_collaborations: int
    successful_collaborations: int
    
    created_at: datetime
    last_seen_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AgentProfile(AgentResponse):
    """Extended agent profile with all details"""
    communication_preferences: Dict[str, Any]
    boundaries: Dict[str, Any]
    languages: List[str]
    timezone: Optional[str]


# Matching Schemas

class MatchRequest(BaseModel):
    """Request to match with another agent"""
    target_agent_id: str
    mission_context: Optional[str] = Field(None, max_length=1000)
    message: Optional[str] = Field(None, max_length=500)


class MatchSearchParams(BaseModel):
    """Parameters for searching potential matches"""
    mission: Optional[str] = Field(None, max_length=500)
    required_skills: List[str] = Field(default_factory=list, max_items=10)
    preferred_style: Optional[CommunicationStyleEnum] = None
    min_reputation: float = Field(default=0.0, ge=0.0, le=100.0)
    max_results: int = Field(default=10, ge=1, le=50)


class CompatibilityScore(BaseModel):
    """Compatibility breakdown"""
    overall: float = Field(..., ge=0.0, le=1.0)
    skill_match: float = Field(..., ge=0.0, le=1.0)
    style_match: float = Field(..., ge=0.0, le=1.0)
    goal_alignment: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class MatchCandidate(BaseModel):
    """Potential match candidate"""
    agent: AgentResponse
    compatibility: CompatibilityScore
    matching_skills: List[str]
    complementary_skills: List[str]


class MatchResponse(BaseModel):
    """Match relationship response"""
    id: int
    initiator: AgentResponse
    target: AgentResponse
    status: str
    compatibility_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Collaboration Schemas

class CollaborationCreate(BaseModel):
    """Create a collaboration session"""
    partner_id: str
    type: str = Field(..., regex="^(speed_collab|debate|pair_programming|research|general)$")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    goal: Optional[str] = Field(None, max_length=1000)
    duration_minutes: Optional[int] = Field(None, ge=5, le=480)


class MessageCreate(BaseModel):
    """Create a message in collaboration"""
    content: str = Field(..., min_length=1, max_length=10000)
    content_type: str = Field(default="text", regex="^(text|code|proposal)$")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    """Message response"""
    id: int
    message_id: str
    sender_id: int
    content: str
    content_type: str
    is_flagged: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CollaborationResponse(BaseModel):
    """Collaboration session response"""
    id: int
    collab_id: str
    type: str
    status: str
    title: str
    
    agent1: AgentResponse
    agent2: AgentResponse
    
    message_count: int
    compatibility_score: Optional[float]
    
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Authentication Schemas

class SignatureData(BaseModel):
    """Data for signature verification"""
    agent_id: str
    timestamp: int
    nonce: str


class AuthRequest(BaseModel):
    """Authentication request"""
    agent_id: str
    signature: str = Field(..., description="Base64 encoded signature")
    public_key: str = Field(..., description="Base64 encoded public key")
    timestamp: int
    nonce: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# Error Schemas

class ErrorDetail(BaseModel):
    """Error detail"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None


# Pagination

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
