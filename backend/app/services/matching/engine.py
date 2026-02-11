"""
Matching engine for AgentNexus
Vector-based agent compatibility scoring using Qdrant with Redis caching.

Computes multi-dimensional compatibility between agents by combining:
- Vector similarity (Qdrant embeddings of skills + bio)
- Skill overlap / complementarity scoring
- Communication style compatibility
- Reputation weighting
"""
import json
import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    Range,
    VectorParams,
)
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CompatibilityResult:
    """Result of a compatibility computation between two agents."""

    agent_id: str
    overall: float
    skill_match: float
    style_match: float
    goal_alignment: float
    matching_skills: list[str]
    complementary_skills: list[str]
    explanation: str


@dataclass(frozen=True)
class AgentVector:
    """Agent data required for vector indexing."""

    agent_id: str
    display_name: str
    skills: list[str]
    embedding: list[float]
    communication_style: str = "balanced"
    formality_level: str = "professional"
    risk_tolerance: str = "moderate"
    reputation_score: float = 0.0
    is_active: bool = True


# Style compatibility matrix: row=agent_a style, col=agent_b style
_STYLE_COMPAT: dict[tuple[str, str], float] = {
    ("concise", "concise"): 0.9,
    ("concise", "balanced"): 0.7,
    ("concise", "detailed"): 0.4,
    ("balanced", "concise"): 0.7,
    ("balanced", "balanced"): 1.0,
    ("balanced", "detailed"): 0.7,
    ("detailed", "concise"): 0.4,
    ("detailed", "balanced"): 0.7,
    ("detailed", "detailed"): 0.9,
}

_FORMALITY_COMPAT: dict[tuple[str, str], float] = {
    ("casual", "casual"): 1.0,
    ("casual", "professional"): 0.6,
    ("casual", "formal"): 0.3,
    ("professional", "casual"): 0.6,
    ("professional", "professional"): 1.0,
    ("professional", "formal"): 0.7,
    ("formal", "casual"): 0.3,
    ("formal", "professional"): 0.7,
    ("formal", "formal"): 1.0,
}

_RISK_COMPAT: dict[tuple[str, str], float] = {
    ("cautious", "cautious"): 1.0,
    ("cautious", "moderate"): 0.7,
    ("cautious", "aggressive"): 0.3,
    ("moderate", "cautious"): 0.7,
    ("moderate", "moderate"): 1.0,
    ("moderate", "aggressive"): 0.6,
    ("aggressive", "cautious"): 0.3,
    ("aggressive", "moderate"): 0.6,
    ("aggressive", "aggressive"): 0.9,
}

# Weights for blending sub-scores into overall compatibility
_W_VECTOR = 0.35
_W_SKILL = 0.30
_W_STYLE = 0.20
_W_REPUTATION = 0.15


def _cache_key(prefix: str, *parts: str) -> str:
    """Build a namespaced Redis cache key."""
    return f"matching:{prefix}:{':'.join(parts)}"


def _compute_skill_scores(
    skills_a: list[str],
    skills_b: list[str],
) -> tuple[float, list[str], list[str]]:
    """Compute skill overlap score and identify matching/complementary skills.

    Returns:
        Tuple of (score 0-1, matching_skills, complementary_skills).
    """
    set_a = {s.lower().strip() for s in skills_a}
    set_b = {s.lower().strip() for s in skills_b}

    if not set_a and not set_b:
        return 0.0, [], []

    intersection = set_a & set_b
    union = set_a | set_b
    jaccard = len(intersection) / len(union) if union else 0.0

    # Complementary = skills one agent has that the other lacks
    complementary = list((set_a - set_b) | (set_b - set_a))

    # Blend overlap with complement bonus (having different skills is valuable)
    complement_ratio = len(complementary) / len(union) if union else 0.0
    score = 0.6 * jaccard + 0.4 * complement_ratio

    return min(score, 1.0), sorted(intersection), sorted(complementary)


def _compute_style_score(
    style_a: str,
    formality_a: str,
    risk_a: str,
    style_b: str,
    formality_b: str,
    risk_b: str,
) -> float:
    """Compute communication style compatibility between two agents."""
    style_score = _STYLE_COMPAT.get(
        (style_a.lower(), style_b.lower()), 0.5
    )
    formality_score = _FORMALITY_COMPAT.get(
        (formality_a.lower(), formality_b.lower()), 0.5
    )
    risk_score = _RISK_COMPAT.get(
        (risk_a.lower(), risk_b.lower()), 0.5
    )
    return 0.4 * style_score + 0.35 * formality_score + 0.25 * risk_score


def _reputation_factor(reputation: float) -> float:
    """Convert reputation (0-100) to a 0-1 factor for scoring."""
    return min(max(reputation / 100.0, 0.0), 1.0)


def _build_explanation(
    overall: float,
    skill_match: float,
    style_match: float,
    goal_alignment: float,
    matching_skills: list[str],
    complementary_skills: list[str],
) -> str:
    """Generate a human-readable explanation of the compatibility score."""
    parts: list[str] = []

    if overall >= 0.8:
        parts.append("Excellent compatibility.")
    elif overall >= 0.6:
        parts.append("Good compatibility.")
    elif overall >= 0.4:
        parts.append("Moderate compatibility.")
    else:
        parts.append("Low compatibility.")

    if matching_skills:
        parts.append(f"Shared skills: {', '.join(matching_skills[:5])}.")
    if complementary_skills:
        parts.append(
            f"Complementary skills: {', '.join(complementary_skills[:5])}."
        )

    if style_match >= 0.8:
        parts.append("Communication styles align well.")
    elif style_match < 0.5:
        parts.append("Communication styles may clash.")

    return " ".join(parts)


class MatchingEngine:
    """Vector-based agent matching engine backed by Qdrant and Redis.

    Responsibilities:
    - Index agent embeddings into Qdrant
    - Find top-K similar agents via vector search
    - Compute multi-factor compatibility scores
    - Cache results in Redis for fast repeat lookups
    """

    def __init__(
        self,
        qdrant: AsyncQdrantClient,
        redis: Redis,
        collection_name: str = settings.QDRANT_COLLECTION_AGENTS,
        vector_dimension: int = settings.VECTOR_DIMENSION,
        similarity_threshold: float = settings.MATCHING_SIMILARITY_THRESHOLD,
        cache_ttl: int = settings.REDIS_CACHE_TTL,
    ) -> None:
        self._qdrant = qdrant
        self._redis = redis
        self._collection = collection_name
        self._vector_dim = vector_dimension
        self._similarity_threshold = similarity_threshold
        self._cache_ttl = cache_ttl

    # ------------------------------------------------------------------
    # Collection management
    # ------------------------------------------------------------------

    async def ensure_collection(self) -> None:
        """Create the Qdrant collection if it does not exist."""
        try:
            await self._qdrant.get_collection(self._collection)
            logger.debug(f"Collection '{self._collection}' already exists")
        except (UnexpectedResponse, Exception):
            await self._qdrant.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=self._vector_dim,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection '{self._collection}'")

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    async def index_agent(self, agent: AgentVector) -> None:
        """Upsert an agent's embedding into the Qdrant collection.

        Args:
            agent: Agent data with embedding vector.

        Raises:
            ValueError: If the embedding dimension does not match the collection.
        """
        if len(agent.embedding) != self._vector_dim:
            raise ValueError(
                f"Embedding dimension {len(agent.embedding)} does not match "
                f"collection dimension {self._vector_dim}"
            )

        point = PointStruct(
            id=hash(agent.agent_id) & 0x7FFFFFFFFFFFFFFF,  # positive int64
            vector=agent.embedding,
            payload={
                "agent_id": agent.agent_id,
                "display_name": agent.display_name,
                "skills": agent.skills,
                "communication_style": agent.communication_style,
                "formality_level": agent.formality_level,
                "risk_tolerance": agent.risk_tolerance,
                "reputation_score": agent.reputation_score,
                "is_active": agent.is_active,
            },
        )

        await self._qdrant.upsert(
            collection_name=self._collection,
            points=[point],
        )
        logger.info(f"Indexed agent '{agent.agent_id}' into Qdrant")

        # Invalidate cached results involving this agent
        await self._invalidate_agent_cache(agent.agent_id)

    async def remove_agent(self, agent_id: str) -> None:
        """Remove an agent's vector from the collection.

        Args:
            agent_id: The unique agent identifier.
        """
        point_id = hash(agent_id) & 0x7FFFFFFFFFFFFFFF
        await self._qdrant.delete(
            collection_name=self._collection,
            points_selector=[point_id],
        )
        logger.info(f"Removed agent '{agent_id}' from Qdrant")
        await self._invalidate_agent_cache(agent_id)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def find_candidates(
        self,
        query_embedding: list[float],
        exclude_agent_id: str | None = None,
        required_skills: list[str] | None = None,
        min_reputation: float = 0.0,
        top_k: int = settings.MATCHING_TOP_K,
    ) -> list[dict]:
        """Find the top-K most similar agents via vector search.

        Args:
            query_embedding: The query vector (e.g. from a mission description).
            exclude_agent_id: Agent ID to exclude from results (self).
            required_skills: If provided, filter to agents with these skills.
            min_reputation: Minimum reputation score filter.
            top_k: Maximum number of results.

        Returns:
            List of dicts with agent payload + similarity score.
        """
        if len(query_embedding) != self._vector_dim:
            raise ValueError(
                f"Query embedding dimension {len(query_embedding)} does not "
                f"match collection dimension {self._vector_dim}"
            )

        # Build Qdrant filters
        must_conditions: list[FieldCondition] = [
            FieldCondition(key="is_active", match=MatchValue(value=True)),
        ]
        if min_reputation > 0:
            must_conditions.append(
                FieldCondition(
                    key="reputation_score",
                    range=Range(gte=min_reputation),
                )
            )

        must_not_conditions: list[FieldCondition] = []
        if exclude_agent_id:
            must_not_conditions.append(
                FieldCondition(
                    key="agent_id",
                    match=MatchValue(value=exclude_agent_id),
                )
            )

        query_filter = Filter(
            must=must_conditions,
            must_not=must_not_conditions if must_not_conditions else None,
        )

        results = await self._qdrant.search(
            collection_name=self._collection,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=self._similarity_threshold,
        )

        candidates = []
        for hit in results:
            payload = hit.payload or {}

            # Post-filter required skills (Qdrant array filtering is limited)
            if required_skills:
                agent_skills = {
                    s.lower() for s in payload.get("skills", [])
                }
                required = {s.lower() for s in required_skills}
                if not required.issubset(agent_skills):
                    continue

            candidates.append(
                {
                    "agent_id": payload.get("agent_id"),
                    "display_name": payload.get("display_name"),
                    "skills": payload.get("skills", []),
                    "communication_style": payload.get(
                        "communication_style", "balanced"
                    ),
                    "formality_level": payload.get(
                        "formality_level", "professional"
                    ),
                    "risk_tolerance": payload.get(
                        "risk_tolerance", "moderate"
                    ),
                    "reputation_score": payload.get("reputation_score", 0.0),
                    "vector_score": hit.score,
                }
            )

        return candidates

    # ------------------------------------------------------------------
    # Compatibility scoring
    # ------------------------------------------------------------------

    async def compute_compatibility(
        self,
        agent_a_id: str,
        agent_a_skills: list[str],
        agent_a_style: str,
        agent_a_formality: str,
        agent_a_risk: str,
        agent_b_id: str,
        agent_b_skills: list[str],
        agent_b_style: str,
        agent_b_formality: str,
        agent_b_risk: str,
        vector_score: float = 0.0,
        agent_b_reputation: float = 0.0,
    ) -> CompatibilityResult:
        """Compute full compatibility between two agents.

        Checks Redis cache first. On miss, computes and caches the result.

        Args:
            agent_a_id: First agent ID.
            agent_a_skills: First agent's skill list.
            agent_a_style: First agent's communication style.
            agent_a_formality: First agent's formality level.
            agent_a_risk: First agent's risk tolerance.
            agent_b_id: Second agent ID.
            agent_b_skills: Second agent's skill list.
            agent_b_style: Second agent's communication style.
            agent_b_formality: Second agent's formality level.
            agent_b_risk: Second agent's risk tolerance.
            vector_score: Pre-computed Qdrant vector similarity (0-1).
            agent_b_reputation: Target agent's reputation (0-100).

        Returns:
            CompatibilityResult with sub-scores and explanation.
        """
        # Symmetric cache key (order-independent)
        pair = tuple(sorted([agent_a_id, agent_b_id]))
        cache_key = _cache_key("compat", pair[0], pair[1])

        # Try cache
        cached = await self._get_cached(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for compatibility {pair}")
            return CompatibilityResult(**cached)

        # Compute sub-scores
        skill_score, matching_skills, complementary_skills = (
            _compute_skill_scores(agent_a_skills, agent_b_skills)
        )
        style_score = _compute_style_score(
            agent_a_style,
            agent_a_formality,
            agent_a_risk,
            agent_b_style,
            agent_b_formality,
            agent_b_risk,
        )
        rep_factor = _reputation_factor(agent_b_reputation)

        # Use vector_score as goal_alignment proxy
        goal_alignment = max(vector_score, 0.0)

        overall = (
            _W_VECTOR * goal_alignment
            + _W_SKILL * skill_score
            + _W_STYLE * style_score
            + _W_REPUTATION * rep_factor
        )
        overall = round(min(max(overall, 0.0), 1.0), 4)

        explanation = _build_explanation(
            overall,
            skill_score,
            style_score,
            goal_alignment,
            matching_skills,
            complementary_skills,
        )

        result = CompatibilityResult(
            agent_id=agent_b_id,
            overall=overall,
            skill_match=round(skill_score, 4),
            style_match=round(style_score, 4),
            goal_alignment=round(goal_alignment, 4),
            matching_skills=matching_skills,
            complementary_skills=complementary_skills,
            explanation=explanation,
        )

        # Cache the result
        await self._set_cached(cache_key, result)
        return result

    async def search_and_rank(
        self,
        query_embedding: list[float],
        requesting_agent_id: str,
        requesting_agent_skills: list[str],
        requesting_agent_style: str = "balanced",
        requesting_agent_formality: str = "professional",
        requesting_agent_risk: str = "moderate",
        required_skills: list[str] | None = None,
        min_reputation: float = 0.0,
        max_results: int = 10,
    ) -> list[CompatibilityResult]:
        """End-to-end search: find candidates via vector search, then rank
        by full compatibility score.

        Args:
            query_embedding: Embedding for the search query / mission.
            requesting_agent_id: ID of the agent performing the search.
            requesting_agent_skills: Skills of the requesting agent.
            requesting_agent_style: Communication style.
            requesting_agent_formality: Formality level.
            requesting_agent_risk: Risk tolerance.
            required_skills: Optional skill filter.
            min_reputation: Minimum reputation filter.
            max_results: Maximum results to return.

        Returns:
            List of CompatibilityResult sorted by overall score descending.
        """
        candidates = await self.find_candidates(
            query_embedding=query_embedding,
            exclude_agent_id=requesting_agent_id,
            required_skills=required_skills,
            min_reputation=min_reputation,
            top_k=settings.MATCHING_TOP_K,
        )

        results: list[CompatibilityResult] = []
        for candidate in candidates:
            result = await self.compute_compatibility(
                agent_a_id=requesting_agent_id,
                agent_a_skills=requesting_agent_skills,
                agent_a_style=requesting_agent_style,
                agent_a_formality=requesting_agent_formality,
                agent_a_risk=requesting_agent_risk,
                agent_b_id=candidate["agent_id"],
                agent_b_skills=candidate["skills"],
                agent_b_style=candidate["communication_style"],
                agent_b_formality=candidate["formality_level"],
                agent_b_risk=candidate["risk_tolerance"],
                vector_score=candidate["vector_score"],
                agent_b_reputation=candidate["reputation_score"],
            )
            results.append(result)

        results.sort(key=lambda r: r.overall, reverse=True)
        return results[:max_results]

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    async def _get_cached(self, key: str) -> Optional[dict]:
        """Get a value from Redis cache, returning None on miss or error."""
        try:
            raw = await self._redis.get(key)
            if raw is not None:
                return json.loads(raw)
        except (RedisError, json.JSONDecodeError) as exc:
            logger.warning(f"Cache read failed for '{key}': {exc}")
        return None

    async def _set_cached(self, key: str, result: CompatibilityResult) -> None:
        """Write a CompatibilityResult to Redis cache."""
        try:
            data = {
                "agent_id": result.agent_id,
                "overall": result.overall,
                "skill_match": result.skill_match,
                "style_match": result.style_match,
                "goal_alignment": result.goal_alignment,
                "matching_skills": result.matching_skills,
                "complementary_skills": result.complementary_skills,
                "explanation": result.explanation,
            }
            await self._redis.set(key, json.dumps(data), ex=self._cache_ttl)
        except RedisError as exc:
            logger.warning(f"Cache write failed for '{key}': {exc}")

    async def _invalidate_agent_cache(self, agent_id: str) -> None:
        """Delete all cached compatibility results involving an agent."""
        try:
            pattern = f"matching:compat:*{agent_id}*"
            cursor = None
            while True:
                cursor, keys = await self._redis.scan(
                    cursor=cursor or 0,
                    match=pattern,
                    count=100,
                )
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
        except RedisError as exc:
            logger.warning(f"Cache invalidation failed for '{agent_id}': {exc}")
