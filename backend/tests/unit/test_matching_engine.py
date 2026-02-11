"""
Tests for the matching engine service.

Covers: vector indexing, candidate search, compatibility scoring,
Redis caching, cache invalidation, and the end-to-end search_and_rank flow.
"""
import json
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from qdrant_client.http.exceptions import UnexpectedResponse
from redis.exceptions import RedisError

from app.services.matching.engine import (
    AgentVector,
    CompatibilityResult,
    MatchingEngine,
    _build_explanation,
    _cache_key,
    _compute_skill_scores,
    _compute_style_score,
    _reputation_factor,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VECTOR_DIM = 384


def _make_embedding(seed: float = 0.1) -> list[float]:
    """Generate a deterministic embedding of the correct dimension."""
    return [seed] * VECTOR_DIM


def _make_agent_vector(
    agent_id: str = "agent-1",
    skills: list[str] | None = None,
    style: str = "balanced",
    formality: str = "professional",
    risk: str = "moderate",
    reputation: float = 50.0,
    embedding: list[float] | None = None,
) -> AgentVector:
    return AgentVector(
        agent_id=agent_id,
        display_name=f"Agent {agent_id}",
        skills=skills or ["python", "ml"],
        embedding=embedding or _make_embedding(),
        communication_style=style,
        formality_level=formality,
        risk_tolerance=risk,
        reputation_score=reputation,
    )


@pytest_asyncio.fixture
async def engine(mock_qdrant, mock_redis):
    """Create a MatchingEngine with mocked dependencies."""
    return MatchingEngine(
        qdrant=mock_qdrant,
        redis=mock_redis,
        collection_name="test_agents",
        vector_dimension=VECTOR_DIM,
        similarity_threshold=0.5,
        cache_ttl=600,
    )


# ---------------------------------------------------------------------------
# Pure function tests
# ---------------------------------------------------------------------------


class TestCacheKey:
    def test_basic_key(self) -> None:
        key = _cache_key("compat", "a1", "a2")
        assert key == "matching:compat:a1:a2"

    def test_single_part(self) -> None:
        key = _cache_key("agent", "abc")
        assert key == "matching:agent:abc"


class TestComputeSkillScores:
    def test_identical_skills(self) -> None:
        score, matching, complementary = _compute_skill_scores(
            ["python", "ml"], ["python", "ml"]
        )
        assert score > 0
        assert matching == ["ml", "python"]
        assert complementary == []

    def test_no_overlap(self) -> None:
        score, matching, complementary = _compute_skill_scores(
            ["python", "ml"], ["rust", "devops"]
        )
        assert matching == []
        assert len(complementary) == 4
        # All skills are complementary → complement_ratio = 1.0
        # jaccard = 0 → score = 0.4 * 1.0 = 0.4
        assert abs(score - 0.4) < 0.01

    def test_partial_overlap(self) -> None:
        score, matching, complementary = _compute_skill_scores(
            ["python", "ml", "fastapi"], ["python", "react", "ml"]
        )
        assert "ml" in matching
        assert "python" in matching
        assert "fastapi" in complementary
        assert "react" in complementary
        assert 0 < score < 1

    def test_empty_skills(self) -> None:
        score, matching, complementary = _compute_skill_scores([], [])
        assert score == 0.0
        assert matching == []
        assert complementary == []

    def test_one_empty(self) -> None:
        score, matching, complementary = _compute_skill_scores(
            ["python"], []
        )
        assert matching == []
        assert complementary == ["python"]

    def test_case_insensitive(self) -> None:
        score, matching, _ = _compute_skill_scores(
            ["Python", "ML"], ["python", "ml"]
        )
        assert "ml" in matching
        assert "python" in matching

    def test_whitespace_stripped(self) -> None:
        _, matching, _ = _compute_skill_scores(
            [" python ", "ml"], ["python", " ml "]
        )
        assert "ml" in matching
        assert "python" in matching


class TestComputeStyleScore:
    def test_perfect_match(self) -> None:
        score = _compute_style_score(
            "balanced", "professional", "moderate",
            "balanced", "professional", "moderate",
        )
        # 0.4*1.0 + 0.35*1.0 + 0.25*1.0 = 1.0
        assert abs(score - 1.0) < 0.01

    def test_worst_match(self) -> None:
        score = _compute_style_score(
            "concise", "casual", "cautious",
            "detailed", "formal", "aggressive",
        )
        # 0.4*0.4 + 0.35*0.3 + 0.25*0.3 = 0.16 + 0.105 + 0.075 = 0.34
        assert abs(score - 0.34) < 0.01

    def test_unknown_values_default(self) -> None:
        score = _compute_style_score(
            "unknown", "unknown", "unknown",
            "unknown", "unknown", "unknown",
        )
        # All lookups miss → default 0.5 each
        # 0.4*0.5 + 0.35*0.5 + 0.25*0.5 = 0.5
        assert abs(score - 0.5) < 0.01


class TestReputationFactor:
    def test_zero(self) -> None:
        assert _reputation_factor(0.0) == 0.0

    def test_fifty(self) -> None:
        assert _reputation_factor(50.0) == 0.5

    def test_hundred(self) -> None:
        assert _reputation_factor(100.0) == 1.0

    def test_over_hundred_clamped(self) -> None:
        assert _reputation_factor(150.0) == 1.0

    def test_negative_clamped(self) -> None:
        assert _reputation_factor(-10.0) == 0.0


class TestBuildExplanation:
    def test_excellent(self) -> None:
        text = _build_explanation(0.85, 0.9, 0.9, 0.8, ["python"], ["rust"])
        assert "Excellent" in text
        assert "python" in text
        assert "rust" in text

    def test_low_style_warning(self) -> None:
        text = _build_explanation(0.3, 0.3, 0.3, 0.3, [], [])
        assert "Low compatibility" in text
        assert "may clash" in text

    def test_good_compatibility(self) -> None:
        text = _build_explanation(0.65, 0.6, 0.7, 0.6, ["ml"], [])
        assert "Good compatibility" in text

    def test_moderate_compatibility(self) -> None:
        text = _build_explanation(0.45, 0.4, 0.6, 0.5, [], ["devops"])
        assert "Moderate compatibility" in text


# ---------------------------------------------------------------------------
# Collection management
# ---------------------------------------------------------------------------


class TestEnsureCollection:
    @pytest.mark.asyncio
    async def test_collection_exists(self, engine, mock_qdrant) -> None:
        mock_qdrant.get_collection.return_value = MagicMock()
        await engine.ensure_collection()
        mock_qdrant.get_collection.assert_awaited_once_with("test_agents")
        mock_qdrant.create_collection.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_collection_created(self, engine, mock_qdrant) -> None:
        import httpx

        mock_qdrant.get_collection.side_effect = UnexpectedResponse(
            status_code=404,
            reason_phrase="Not Found",
            content=b"",
            headers=httpx.Headers(),
        )
        await engine.ensure_collection()
        mock_qdrant.create_collection.assert_awaited_once()


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------


class TestIndexAgent:
    @pytest.mark.asyncio
    async def test_index_success(self, engine, mock_qdrant) -> None:
        agent = _make_agent_vector()
        await engine.index_agent(agent)

        mock_qdrant.upsert.assert_awaited_once()
        call_kwargs = mock_qdrant.upsert.call_args
        assert call_kwargs.kwargs["collection_name"] == "test_agents"

        point = call_kwargs.kwargs["points"][0]
        assert point.payload["agent_id"] == "agent-1"
        assert point.payload["skills"] == ["python", "ml"]
        assert point.payload["is_active"] is True

    @pytest.mark.asyncio
    async def test_wrong_dimension_raises(self, engine) -> None:
        agent = _make_agent_vector(embedding=[0.1] * 10)
        with pytest.raises(ValueError, match="dimension"):
            await engine.index_agent(agent)

    @pytest.mark.asyncio
    async def test_index_invalidates_cache(
        self, engine, mock_redis
    ) -> None:
        agent = _make_agent_vector()
        await engine.index_agent(agent)
        # scan should have been called for cache invalidation
        mock_redis.scan.assert_awaited()


class TestRemoveAgent:
    @pytest.mark.asyncio
    async def test_remove_success(self, engine, mock_qdrant, mock_redis) -> None:
        await engine.remove_agent("agent-1")
        mock_qdrant.delete.assert_awaited_once()
        mock_redis.scan.assert_awaited()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@dataclass
class _FakeHit:
    """Mimics a Qdrant ScoredPoint."""
    score: float
    payload: dict


class TestFindCandidates:
    @pytest.mark.asyncio
    async def test_returns_candidates(self, engine, mock_qdrant) -> None:
        mock_qdrant.search.return_value = [
            _FakeHit(
                score=0.9,
                payload={
                    "agent_id": "agent-2",
                    "display_name": "Agent 2",
                    "skills": ["python", "ml"],
                    "communication_style": "balanced",
                    "formality_level": "professional",
                    "risk_tolerance": "moderate",
                    "reputation_score": 80.0,
                    "is_active": True,
                },
            )
        ]

        results = await engine.find_candidates(
            query_embedding=_make_embedding(),
            exclude_agent_id="agent-1",
        )

        assert len(results) == 1
        assert results[0]["agent_id"] == "agent-2"
        assert results[0]["vector_score"] == 0.9

    @pytest.mark.asyncio
    async def test_empty_results(self, engine, mock_qdrant) -> None:
        mock_qdrant.search.return_value = []
        results = await engine.find_candidates(
            query_embedding=_make_embedding(),
        )
        assert results == []

    @pytest.mark.asyncio
    async def test_wrong_dimension_raises(self, engine) -> None:
        with pytest.raises(ValueError, match="dimension"):
            await engine.find_candidates(query_embedding=[0.1] * 10)

    @pytest.mark.asyncio
    async def test_required_skills_filter(self, engine, mock_qdrant) -> None:
        mock_qdrant.search.return_value = [
            _FakeHit(
                score=0.85,
                payload={
                    "agent_id": "agent-2",
                    "display_name": "Agent 2",
                    "skills": ["python", "ml"],
                    "is_active": True,
                },
            ),
            _FakeHit(
                score=0.80,
                payload={
                    "agent_id": "agent-3",
                    "display_name": "Agent 3",
                    "skills": ["rust", "devops"],
                    "is_active": True,
                },
            ),
        ]

        results = await engine.find_candidates(
            query_embedding=_make_embedding(),
            required_skills=["python"],
        )

        # agent-3 should be filtered out (no python skill)
        assert len(results) == 1
        assert results[0]["agent_id"] == "agent-2"

    @pytest.mark.asyncio
    async def test_min_reputation_filter(self, engine, mock_qdrant) -> None:
        """Verify that min_reputation is passed to Qdrant filter."""
        mock_qdrant.search.return_value = []

        await engine.find_candidates(
            query_embedding=_make_embedding(),
            min_reputation=50.0,
        )

        call_kwargs = mock_qdrant.search.call_args.kwargs
        query_filter = call_kwargs["query_filter"]
        # Should have is_active + reputation_score conditions
        assert len(query_filter.must) == 2


# ---------------------------------------------------------------------------
# Compatibility scoring
# ---------------------------------------------------------------------------


class TestComputeCompatibility:
    @pytest.mark.asyncio
    async def test_basic_compatibility(self, engine) -> None:
        result = await engine.compute_compatibility(
            agent_a_id="agent-1",
            agent_a_skills=["python", "ml"],
            agent_a_style="balanced",
            agent_a_formality="professional",
            agent_a_risk="moderate",
            agent_b_id="agent-2",
            agent_b_skills=["python", "devops"],
            agent_b_style="balanced",
            agent_b_formality="professional",
            agent_b_risk="moderate",
            vector_score=0.85,
            agent_b_reputation=70.0,
        )

        assert isinstance(result, CompatibilityResult)
        assert 0 <= result.overall <= 1
        assert 0 <= result.skill_match <= 1
        assert 0 <= result.style_match <= 1
        assert 0 <= result.goal_alignment <= 1
        assert result.agent_id == "agent-2"
        assert "python" in result.matching_skills
        assert len(result.explanation) > 0

    @pytest.mark.asyncio
    async def test_cache_write(self, engine, mock_redis) -> None:
        await engine.compute_compatibility(
            agent_a_id="agent-1",
            agent_a_skills=["python"],
            agent_a_style="balanced",
            agent_a_formality="professional",
            agent_a_risk="moderate",
            agent_b_id="agent-2",
            agent_b_skills=["python"],
            agent_b_style="balanced",
            agent_b_formality="professional",
            agent_b_risk="moderate",
            vector_score=0.8,
            agent_b_reputation=50.0,
        )

        mock_redis.set.assert_awaited_once()
        call_args = mock_redis.set.call_args
        # Key should contain both agent IDs (sorted)
        assert "agent-1" in call_args.args[0]
        assert "agent-2" in call_args.args[0]
        # Value should be valid JSON
        stored = json.loads(call_args.args[1])
        assert "overall" in stored
        assert "skill_match" in stored

    @pytest.mark.asyncio
    async def test_cache_hit(self, engine, mock_redis) -> None:
        cached_data = {
            "agent_id": "agent-2",
            "overall": 0.75,
            "skill_match": 0.6,
            "style_match": 0.8,
            "goal_alignment": 0.7,
            "matching_skills": ["python"],
            "complementary_skills": ["rust"],
            "explanation": "Good compatibility.",
        }
        mock_redis.get.return_value = json.dumps(cached_data)

        result = await engine.compute_compatibility(
            agent_a_id="agent-1",
            agent_a_skills=["python"],
            agent_a_style="balanced",
            agent_a_formality="professional",
            agent_a_risk="moderate",
            agent_b_id="agent-2",
            agent_b_skills=["python"],
            agent_b_style="balanced",
            agent_b_formality="professional",
            agent_b_risk="moderate",
            vector_score=0.8,
            agent_b_reputation=50.0,
        )

        assert result.overall == 0.75
        assert result.matching_skills == ["python"]
        # Should NOT have written to cache (cache hit)
        mock_redis.set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_symmetric_cache_key(self, engine, mock_redis) -> None:
        """Cache key should be the same regardless of agent order."""
        mock_redis.get.return_value = None

        await engine.compute_compatibility(
            agent_a_id="agent-2",
            agent_a_skills=["python"],
            agent_a_style="balanced",
            agent_a_formality="professional",
            agent_a_risk="moderate",
            agent_b_id="agent-1",
            agent_b_skills=["python"],
            agent_b_style="balanced",
            agent_b_formality="professional",
            agent_b_risk="moderate",
            vector_score=0.8,
            agent_b_reputation=50.0,
        )

        set_call = mock_redis.set.call_args
        key = set_call.args[0]
        # Sorted order: agent-1 comes before agent-2
        assert key == "matching:compat:agent-1:agent-2"

    @pytest.mark.asyncio
    async def test_zero_vector_score(self, engine) -> None:
        result = await engine.compute_compatibility(
            agent_a_id="agent-1",
            agent_a_skills=[],
            agent_a_style="concise",
            agent_a_formality="casual",
            agent_a_risk="cautious",
            agent_b_id="agent-2",
            agent_b_skills=[],
            agent_b_style="detailed",
            agent_b_formality="formal",
            agent_b_risk="aggressive",
            vector_score=0.0,
            agent_b_reputation=0.0,
        )

        assert result.overall >= 0.0
        assert result.goal_alignment == 0.0


class TestCacheResilience:
    @pytest.mark.asyncio
    async def test_redis_get_error(self, engine, mock_redis) -> None:
        """Engine should work even when Redis read fails."""
        mock_redis.get.side_effect = RedisError("connection refused")

        result = await engine.compute_compatibility(
            agent_a_id="agent-1",
            agent_a_skills=["python"],
            agent_a_style="balanced",
            agent_a_formality="professional",
            agent_a_risk="moderate",
            agent_b_id="agent-2",
            agent_b_skills=["python"],
            agent_b_style="balanced",
            agent_b_formality="professional",
            agent_b_risk="moderate",
            vector_score=0.8,
            agent_b_reputation=50.0,
        )

        # Should still compute a valid result despite cache error
        assert isinstance(result, CompatibilityResult)
        assert result.overall > 0

    @pytest.mark.asyncio
    async def test_redis_set_error(self, engine, mock_redis) -> None:
        """Engine should not raise when Redis write fails."""
        mock_redis.set.side_effect = RedisError("connection refused")

        # Should complete without raising
        result = await engine.compute_compatibility(
            agent_a_id="agent-1",
            agent_a_skills=["python"],
            agent_a_style="balanced",
            agent_a_formality="professional",
            agent_a_risk="moderate",
            agent_b_id="agent-2",
            agent_b_skills=["python"],
            agent_b_style="balanced",
            agent_b_formality="professional",
            agent_b_risk="moderate",
            vector_score=0.8,
            agent_b_reputation=50.0,
        )

        assert isinstance(result, CompatibilityResult)

    @pytest.mark.asyncio
    async def test_redis_scan_error_on_invalidation(
        self, engine, mock_qdrant, mock_redis
    ) -> None:
        """Cache invalidation failure should not break indexing."""
        mock_redis.scan.side_effect = RedisError("connection refused")

        agent = _make_agent_vector()
        # Should not raise
        await engine.index_agent(agent)
        mock_qdrant.upsert.assert_awaited_once()


# ---------------------------------------------------------------------------
# End-to-end: search_and_rank
# ---------------------------------------------------------------------------


class TestSearchAndRank:
    @pytest.mark.asyncio
    async def test_full_pipeline(self, engine, mock_qdrant) -> None:
        mock_qdrant.search.return_value = [
            _FakeHit(
                score=0.95,
                payload={
                    "agent_id": "agent-best",
                    "display_name": "Best Agent",
                    "skills": ["python", "ml", "fastapi"],
                    "communication_style": "balanced",
                    "formality_level": "professional",
                    "risk_tolerance": "moderate",
                    "reputation_score": 90.0,
                    "is_active": True,
                },
            ),
            _FakeHit(
                score=0.70,
                payload={
                    "agent_id": "agent-ok",
                    "display_name": "OK Agent",
                    "skills": ["rust", "devops"],
                    "communication_style": "concise",
                    "formality_level": "casual",
                    "risk_tolerance": "aggressive",
                    "reputation_score": 30.0,
                    "is_active": True,
                },
            ),
        ]

        results = await engine.search_and_rank(
            query_embedding=_make_embedding(),
            requesting_agent_id="agent-me",
            requesting_agent_skills=["python", "ml"],
            requesting_agent_style="balanced",
            requesting_agent_formality="professional",
            requesting_agent_risk="moderate",
            max_results=10,
        )

        assert len(results) == 2
        # Best agent should rank higher (better skill overlap + reputation + style)
        assert results[0].agent_id == "agent-best"
        assert results[0].overall > results[1].overall
        assert "python" in results[0].matching_skills

    @pytest.mark.asyncio
    async def test_max_results_limit(self, engine, mock_qdrant) -> None:
        mock_qdrant.search.return_value = [
            _FakeHit(
                score=0.9 - i * 0.05,
                payload={
                    "agent_id": f"agent-{i}",
                    "display_name": f"Agent {i}",
                    "skills": ["python"],
                    "communication_style": "balanced",
                    "formality_level": "professional",
                    "risk_tolerance": "moderate",
                    "reputation_score": 50.0,
                    "is_active": True,
                },
            )
            for i in range(5)
        ]

        results = await engine.search_and_rank(
            query_embedding=_make_embedding(),
            requesting_agent_id="agent-me",
            requesting_agent_skills=["python"],
            max_results=3,
        )

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_no_candidates(self, engine, mock_qdrant) -> None:
        mock_qdrant.search.return_value = []

        results = await engine.search_and_rank(
            query_embedding=_make_embedding(),
            requesting_agent_id="agent-me",
            requesting_agent_skills=["python"],
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_results_sorted_descending(
        self, engine, mock_qdrant
    ) -> None:
        mock_qdrant.search.return_value = [
            _FakeHit(
                score=0.6,
                payload={
                    "agent_id": "agent-low",
                    "display_name": "Low",
                    "skills": ["rust"],
                    "communication_style": "detailed",
                    "formality_level": "formal",
                    "risk_tolerance": "cautious",
                    "reputation_score": 10.0,
                    "is_active": True,
                },
            ),
            _FakeHit(
                score=0.95,
                payload={
                    "agent_id": "agent-high",
                    "display_name": "High",
                    "skills": ["python", "ml"],
                    "communication_style": "balanced",
                    "formality_level": "professional",
                    "risk_tolerance": "moderate",
                    "reputation_score": 95.0,
                    "is_active": True,
                },
            ),
        ]

        results = await engine.search_and_rank(
            query_embedding=_make_embedding(),
            requesting_agent_id="agent-me",
            requesting_agent_skills=["python", "ml"],
        )

        scores = [r.overall for r in results]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# AgentVector dataclass
# ---------------------------------------------------------------------------


class TestAgentVector:
    def test_frozen(self) -> None:
        agent = _make_agent_vector()
        with pytest.raises(AttributeError):
            agent.agent_id = "changed"  # type: ignore[misc]

    def test_defaults(self) -> None:
        agent = AgentVector(
            agent_id="a",
            display_name="A",
            skills=[],
            embedding=[0.0],
        )
        assert agent.communication_style == "balanced"
        assert agent.formality_level == "professional"
        assert agent.risk_tolerance == "moderate"
        assert agent.reputation_score == 0.0
        assert agent.is_active is True


class TestCompatibilityResult:
    def test_frozen(self) -> None:
        result = CompatibilityResult(
            agent_id="a",
            overall=0.5,
            skill_match=0.5,
            style_match=0.5,
            goal_alignment=0.5,
            matching_skills=[],
            complementary_skills=[],
            explanation="test",
        )
        with pytest.raises(AttributeError):
            result.overall = 0.9  # type: ignore[misc]
