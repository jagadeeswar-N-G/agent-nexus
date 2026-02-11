"""
Configuration settings for AgentNexus
Manages environment variables and application settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    APP_NAME: str = "AgentNexus"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "Ed25519"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://agentnexus.dev",
        "https://www.agentnexus.dev"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://agentnexus:dev_password@localhost:5432/agent_nexus"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Qdrant Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_AGENTS: str = "agents"
    QDRANT_COLLECTION_SKILLS: str = "skills"
    VECTOR_DIMENSION: int = 384  # sentence-transformers/all-MiniLM-L6-v2
    
    # MinIO / S3
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    S3_BUCKET_ARTIFACTS: str = "agent-artifacts"
    S3_BUCKET_AVATARS: str = "agent-avatars"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # Agent Settings
    MAX_AGENTS_PER_USER: int = 5
    MAX_PROFILE_BIO_LENGTH: int = 2000
    MAX_SKILLS_PER_AGENT: int = 50
    MAX_ACTIVE_MATCHES: int = 20
    MAX_CONCURRENT_COLLABORATIONS: int = 5
    
    # Matching Algorithm
    MATCHING_BATCH_SIZE: int = 100
    MATCHING_SIMILARITY_THRESHOLD: float = 0.7
    MATCHING_TOP_K: int = 50
    
    # Collaboration
    COLLAB_MAX_DURATION_MINUTES: int = 480  # 8 hours
    COLLAB_SPEED_DURATION_MINUTES: int = 5
    COLLAB_MESSAGE_MAX_LENGTH: int = 10000
    COLLAB_RATE_LIMIT_PER_MINUTE: int = 30
    
    # WebSockets
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS_PER_AGENT: int = 3
    
    # External APIs
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "noreply@agentnexus.dev"
    EMAILS_FROM_NAME: str = "AgentNexus"
    
    # Feature Flags
    FEATURE_SPEED_COLLAB: bool = True
    FEATURE_DEBATE_ARENA: bool = False
    FEATURE_GROUP_SQUADS: bool = False
    FEATURE_API_ONLY_MODE: bool = True
    
    @property
    def async_database_url(self) -> str:
        """Get async database URL"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"


settings = Settings()
