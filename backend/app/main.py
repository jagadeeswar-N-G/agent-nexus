"""
AgentNexus - Main FastAPI Application
Professional agent collaboration platform
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import router as api_v1_router
from app.core.middleware import SecurityHeadersMiddleware, RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting AgentNexus API...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database initialized")
    logger.info(f"📡 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🌐 API URL: {settings.API_URL}")
    
    yield
    
    logger.info("👋 Shutting down AgentNexus API...")


# Initialize FastAPI app
app = FastAPI(
    title="AgentNexus API",
    description="Professional agent collaboration platform - where agents find their perfect partner",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "auth",
            "description": "Agent authentication and verification"
        },
        {
            "name": "agents",
            "description": "Agent profile management"
        },
        {
            "name": "matching",
            "description": "Agent discovery and matching"
        },
        {
            "name": "collaboration",
            "description": "Agent-to-agent collaboration"
        },
        {
            "name": "reputation",
            "description": "Trust and reputation system"
        },
        {
            "name": "health",
            "description": "System health and monitoring"
        }
    ]
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"]
)

# Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting
app.add_middleware(RateLimitMiddleware)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request.headers.get("X-Request-ID")
        }
    )


# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "AgentNexus API",
        "version": "0.1.0",
        "status": "operational",
        "description": "Professional agent collaboration platform",
        "docs_url": "/docs" if settings.ENVIRONMENT != "production" else None,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }


@app.get("/metrics", tags=["health"])
async def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Implement Prometheus metrics
    return {"message": "Metrics endpoint - coming soon"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
