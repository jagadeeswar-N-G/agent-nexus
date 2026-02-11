"""
Demo script to test the matching engine locally without external services.
Uses mock clients to demonstrate functionality.
"""
import asyncio
from unittest.mock import AsyncMock

from app.services.matching import AgentVector, MatchingEngine


async def main():
    """Demonstrate matching engine functionality."""
    print("🚀 AgentNexus Matching Engine Demo\n")
    print("=" * 60)

    # Create mock clients (no real Redis or Qdrant needed)
    mock_qdrant = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # Cache miss
    mock_redis.set.return_value = True

    # Initialize matching engine
    engine = MatchingEngine(
        qdrant=mock_qdrant,
        redis=mock_redis,
        collection_name="demo_agents",
        vector_dimension=384,
    )

    print("✅ Matching engine initialized\n")

    # Create sample agent vectors
    agent_a = AgentVector(
        agent_id="agent-001",
        display_name="Python AI Expert",
        skills=["python", "machine-learning", "fastapi", "pytorch"],
        embedding=[0.1] * 384,  # Mock embedding
        communication_style="balanced",
        formality_level="professional",
        risk_tolerance="moderate",
        reputation_score=85.0,
    )

    agent_b = AgentVector(
        agent_id="agent-002",
        display_name="Full-Stack Dev",
        skills=["python", "react", "fastapi", "postgresql"],
        embedding=[0.12] * 384,  # Mock embedding
        communication_style="balanced",
        formality_level="professional",
        risk_tolerance="moderate",
        reputation_score=78.0,
    )

    agent_c = AgentVector(
        agent_id="agent-003",
        display_name="Rust Systems Engineer",
        skills=["rust", "systems-programming", "performance", "networking"],
        embedding=[0.05] * 384,  # Different embedding
        communication_style="concise",
        formality_level="casual",
        risk_tolerance="aggressive",
        reputation_score=92.0,
    )

    print("📊 Sample Agents:")
    print(f"  • {agent_a.display_name}: {', '.join(agent_a.skills[:3])}")
    print(f"  • {agent_b.display_name}: {', '.join(agent_b.skills[:3])}")
    print(f"  • {agent_c.display_name}: {', '.join(agent_c.skills[:3])}")
    print()

    # Compute compatibility between agents
    print("🔍 Computing Compatibility Scores...\n")

    # Agent A vs Agent B (similar skills, same style)
    result_ab = await engine.compute_compatibility(
        agent_a_id=agent_a.agent_id,
        agent_a_skills=agent_a.skills,
        agent_a_style=agent_a.communication_style,
        agent_a_formality=agent_a.formality_level,
        agent_a_risk=agent_a.risk_tolerance,
        agent_b_id=agent_b.agent_id,
        agent_b_skills=agent_b.skills,
        agent_b_style=agent_b.communication_style,
        agent_b_formality=agent_b.formality_level,
        agent_b_risk=agent_b.risk_tolerance,
        vector_score=0.88,  # High similarity
        agent_b_reputation=agent_b.reputation_score,
    )

    print(f"1️⃣  {agent_a.display_name} ↔️  {agent_b.display_name}")
    print(f"   Overall Score: {result_ab.overall:.2%}")
    print(f"   • Skill Match: {result_ab.skill_match:.2%}")
    print(f"   • Style Match: {result_ab.style_match:.2%}")
    print(f"   • Goal Alignment: {result_ab.goal_alignment:.2%}")
    print(f"   • Matching Skills: {', '.join(result_ab.matching_skills)}")
    print(f"   • Explanation: {result_ab.explanation}")
    print()

    # Agent A vs Agent C (different skills, different style)
    result_ac = await engine.compute_compatibility(
        agent_a_id=agent_a.agent_id,
        agent_a_skills=agent_a.skills,
        agent_a_style=agent_a.communication_style,
        agent_a_formality=agent_a.formality_level,
        agent_a_risk=agent_a.risk_tolerance,
        agent_b_id=agent_c.agent_id,
        agent_b_skills=agent_c.skills,
        agent_b_style=agent_c.communication_style,
        agent_b_formality=agent_c.formality_level,
        agent_b_risk=agent_c.risk_tolerance,
        vector_score=0.35,  # Low similarity
        agent_b_reputation=agent_c.reputation_score,
    )

    print(f"2️⃣  {agent_a.display_name} ↔️  {agent_c.display_name}")
    print(f"   Overall Score: {result_ac.overall:.2%}")
    print(f"   • Skill Match: {result_ac.skill_match:.2%}")
    print(f"   • Style Match: {result_ac.style_match:.2%}")
    print(f"   • Goal Alignment: {result_ac.goal_alignment:.2%}")
    print(f"   • Matching Skills: {', '.join(result_ac.matching_skills) if result_ac.matching_skills else 'None'}")
    print(f"   • Explanation: {result_ac.explanation}")
    print()

    print("=" * 60)
    print("✅ Demo complete! The matching engine works without external services.")
    print("\n💡 Key Insights:")
    print("   • Agent A & B: High compatibility (88% vector, shared skills, same style)")
    print("   • Agent A & C: Lower compatibility (35% vector, no shared skills, different style)")
    print("\n📝 Note: This demo uses mock Redis/Qdrant. In production, you'd connect to real services.")


if __name__ == "__main__":
    asyncio.run(main())
