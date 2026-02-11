"""
Database models for AgentNexus
SQLAlchemy ORM models for agents, profiles, matches, and collaborations
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum, Float, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum

from app.core.database import Base


class AgentStatus(str, enum.Enum):
    """Agent account status"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class VerificationLevel(str, enum.Enum):
    """Agent verification level"""
    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified"
    CRYPTO_VERIFIED = "crypto_verified"
    PLATFORM_VERIFIED = "platform_verified"


class CommunicationStyle(str, enum.Enum):
    """Communication style preferences"""
    CONCISE = "concise"
    DETAILED = "detailed"
    BALANCED = "balanced"


class FormalityLevel(str, enum.Enum):
    """Formality level"""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FORMAL = "formal"


class RiskTolerance(str, enum.Enum):
    """Risk tolerance for actions"""
    CAUTIOUS = "cautious"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class Agent(Base):
    """Core agent model"""
    __tablename__ = "agents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agent_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    # Identity
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    handle: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    tagline: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Cryptographic Identity
    public_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    key_algorithm: Mapped[str] = mapped_column(String(50), default="Ed25519")
    verification_level: Mapped[VerificationLevel] = mapped_column(
        Enum(VerificationLevel), 
        default=VerificationLevel.UNVERIFIED
    )
    
    # Runtime & Platform
    runtime_type: Mapped[Optional[str]] = mapped_column(String(50))  # langchain, autogpt, custom
    runtime_version: Mapped[Optional[str]] = mapped_column(String(50))
    platform_provider: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Status
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus), 
        default=AgentStatus.PENDING
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Skills & Capabilities
    skills: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    capabilities: Mapped[dict] = mapped_column(JSONB, default=dict)  # {browser: true, filesystem: false}
    languages: Mapped[List[str]] = mapped_column(ARRAY(String), default=["en"])
    
    # Communication Preferences
    communication_style: Mapped[CommunicationStyle] = mapped_column(
        Enum(CommunicationStyle),
        default=CommunicationStyle.BALANCED
    )
    formality_level: Mapped[FormalityLevel] = mapped_column(
        Enum(FormalityLevel),
        default=FormalityLevel.PROFESSIONAL
    )
    risk_tolerance: Mapped[RiskTolerance] = mapped_column(
        Enum(RiskTolerance),
        default=RiskTolerance.MODERATE
    )
    
    # Boundaries & Preferences
    boundaries: Mapped[dict] = mapped_column(JSONB, default=dict)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    availability_hours: Mapped[Optional[dict]] = mapped_column(JSONB)  # {start: "09:00", end: "17:00"}
    
    # Reputation
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_collaborations: Mapped[int] = mapped_column(Integer, default=0)
    successful_collaborations: Mapped[int] = mapped_column(Integer, default=0)
    total_matches: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    matches_initiated: Mapped[List["Match"]] = relationship(
        "Match", 
        foreign_keys="Match.initiator_id",
        back_populates="initiator"
    )
    matches_received: Mapped[List["Match"]] = relationship(
        "Match",
        foreign_keys="Match.target_id",
        back_populates="target"
    )
    collaborations_as_agent1: Mapped[List["Collaboration"]] = relationship(
        "Collaboration",
        foreign_keys="Collaboration.agent1_id",
        back_populates="agent1"
    )
    collaborations_as_agent2: Mapped[List["Collaboration"]] = relationship(
        "Collaboration",
        foreign_keys="Collaboration.agent2_id",
        back_populates="agent2"
    )
    
    __table_args__ = (
        Index('ix_agents_status_active', 'status', 'is_active'),
        Index('ix_agents_reputation', 'reputation_score'),
        CheckConstraint('reputation_score >= 0.0 AND reputation_score <= 100.0', name='valid_reputation'),
    )


class MatchStatus(str, enum.Enum):
    """Match status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Match(Base):
    """Agent matching/pairing"""
    __tablename__ = "matches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Agents
    initiator_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Status
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), default=MatchStatus.PENDING)
    
    # Match Details
    compatibility_score: Mapped[float] = mapped_column(Float)
    compatibility_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict)
    mission_context: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    initiator: Mapped[Agent] = relationship("Agent", foreign_keys=[initiator_id], back_populates="matches_initiated")
    target: Mapped[Agent] = relationship("Agent", foreign_keys=[target_id], back_populates="matches_received")
    
    __table_args__ = (
        UniqueConstraint('initiator_id', 'target_id', name='unique_match_pair'),
        Index('ix_matches_status', 'status'),
        Index('ix_matches_target_status', 'target_id', 'status'),
        CheckConstraint('initiator_id != target_id', name='no_self_match'),
    )


class CollaborationType(str, enum.Enum):
    """Type of collaboration"""
    SPEED_COLLAB = "speed_collab"
    DEBATE = "debate"
    PAIR_PROGRAMMING = "pair_programming"
    RESEARCH = "research"
    GENERAL = "general"


class CollaborationStatus(str, enum.Enum):
    """Collaboration status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Collaboration(Base):
    """Agent collaboration session"""
    __tablename__ = "collaborations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    collab_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    # Agents
    agent1_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), nullable=False)
    agent2_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Collaboration Details
    type: Mapped[CollaborationType] = mapped_column(Enum(CollaborationType), nullable=False)
    status: Mapped[CollaborationStatus] = mapped_column(
        Enum(CollaborationStatus),
        default=CollaborationStatus.PENDING
    )
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    goal: Mapped[Optional[str]] = mapped_column(Text)
    
    # Activity
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    artifact_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metrics
    compatibility_score: Mapped[Optional[float]] = mapped_column(Float)
    success_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5
    agent1_rating: Mapped[Optional[int]] = mapped_column(Integer)
    agent2_rating: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    agent1: Mapped[Agent] = relationship("Agent", foreign_keys=[agent1_id], back_populates="collaborations_as_agent1")
    agent2: Mapped[Agent] = relationship("Agent", foreign_keys=[agent2_id], back_populates="collaborations_as_agent2")
    
    __table_args__ = (
        Index('ix_collaborations_status', 'status'),
        Index('ix_collaborations_type', 'type'),
        Index('ix_collaborations_agents', 'agent1_id', 'agent2_id'),
        CheckConstraint('agent1_id != agent2_id', name='no_self_collaboration'),
        CheckConstraint('success_rating >= 1 AND success_rating <= 5', name='valid_success_rating'),
    )


class Message(Base):
    """Collaboration message"""
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    collaboration_id: Mapped[int] = mapped_column(Integer, ForeignKey("collaborations.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), nullable=False)
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="text")  # text, code, proposal
    
    # Safety Flags
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    flag_reason: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_messages_collaboration', 'collaboration_id', 'created_at'),
        Index('ix_messages_sender', 'sender_id'),
    )
