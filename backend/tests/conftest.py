"""
Shared pytest fixtures for AgentNexus backend tests.
"""
import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_redis() -> AsyncGenerator[AsyncMock, None]:
    """Provide a mocked async Redis client."""
    redis = AsyncMock(spec=Redis)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.scan = AsyncMock(return_value=(0, []))
    yield redis


@pytest_asyncio.fixture
async def mock_qdrant() -> AsyncGenerator[AsyncMock, None]:
    """Provide a mocked async Qdrant client."""
    qdrant = AsyncMock(spec=AsyncQdrantClient)
    qdrant.get_collection = AsyncMock()
    qdrant.create_collection = AsyncMock()
    qdrant.upsert = AsyncMock()
    qdrant.delete = AsyncMock()
    qdrant.search = AsyncMock(return_value=[])
    yield qdrant
