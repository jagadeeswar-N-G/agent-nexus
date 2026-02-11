"""
Main API v1 Router
Aggregates all v1 endpoint routers
"""
from fastapi import APIRouter

from app.api.v1 import auth, agents, matching, collaborations

# Create main v1 router
router = APIRouter()

# Include all sub-routers
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(matching.router, prefix="/matching", tags=["matching"])
router.include_router(collaborations.router, prefix="/collaborations", tags=["collaboration"])
