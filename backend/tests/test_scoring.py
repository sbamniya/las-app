"""Tests for CAITO, GSTI, and ROI scoring engines."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.scoring.caito_engine import CAITOEngine
from app.scoring.gsti_engine import GSTIEngine
from app.scoring.roi_engine import ROIEngine, WorkflowPerformance, BusinessOutcome


def test_caito_basic():
    engine = CAITOEngine(transformation_goal="digital_transformation")
    scores = {
        "culture": {"leadership_commitment": 0.8, "change_capacity": 0.7, "innovation_culture": 0.6,
                     "risk_tolerance": 0.5, "ai_vision_clarity": 0.7, "cross_functional_collaboration": 0.6,
                     "data_driven_decision_making": 0.75},
        "architecture": {"cloud_maturity": 0.9, "api_availability": 0.8, "data_infrastructure": 0.7,
                          "security_posture": 0.85, "scalability": 0.75, "integration_readiness": 0.7,
                          "compute_capacity": 0.8},
        "integration": {"system_connectivity": 0.6, "data_quality": 0.5, "workflow_automation": 0.4,
                         "mcp_readiness": 0.3, "api_coverage": 0.55, "real_time_data_flow": 0.45,
                         "interoperability": 0.5},
        "talent": {"skill_distribution": 0.7, "learning_velocity": 0.65, "ai_literacy": 0.5,
                    "adaptability": 0.6, "technical_depth": 0.55, "change_readiness": 0.6,
                    "agent_collaboration_skills": 0.4},
    }
    result = engine.calculate(scores)
    assert 0.0 <= result.overall_score <= 1.0
    assert result.grade in ["A", "B", "C", "D", "F"]
    assert len(result.pillars) == 4
    assert result.confidence > 0
    print(f"CAITO Score: {result.overall_score} (Grade: {result.grade})")
    print(f"Pillars: {', '.join(f'{k}={v.raw_score:.3f}' for k, v in result.pillars.items())}")
    print(f"Gaps: {len(result.gaps)}, Opportunities: {len(result.opportunities)}")


def test_caito_simulation():
    engine = CAITOEngine(transformation_goal="automation")
    scores = {
        "culture": {"leadership_commitment": 0.5, "change_capacity": 0.4},
        "architecture": {"cloud_maturity": 0.6, "api_availability": 0.5},
        "integration": {"system_connectivity": 0.3, "data_quality": 0.3},
        "talent": {"skill_distribution": 0.5, "ai_literacy": 0.4},
    }
    original = engine.calculate(scores)
    simulated = engine.simulate(original, {"integration": {"system_connectivity": 0.20, "data_quality": 0.20}})
    assert simulated.overall_score >= original.overall_score
    print(f"Original: {original.overall_score:.4f} -> Simulated: {simulated.overall_score:.4f}")
    print(f"Delta: +{simulated.overall_score - original.overall_score:.4f}")


def test_gsti_agent_scoring():
    engine = GSTIEngine()
    agent = engine.score_agent(
        agent_id="equity-extractor",
        accuracy=0.92,
        confidence=0.88,
        latency_normalized=0.85,
        cost_efficiency=0.90,
        threshold_failures=0,
    )
    assert agent.classification == "execute"
    assert agent.raw_score >= 0.55
    print(f"Agent '{agent.agent_id}': Score={agent.raw_score}, Class={agent.classification}, Grade={agent.grade}")

    # Test suppression
    bad_agent = engine.score_agent("bad-agent", 0.2, 0.15, 0.3, 0.4, 3)
    assert bad_agent.classification == "suppress"
    print(f"Agent '{bad_agent.agent_id}': Score={bad_agent.raw_score}, Class={bad_agent.classification}")


def test_gsti_full():
    engine = GSTIEngine(deployment_context="agent_deployment")
    result = engine.calculate(
        culture_trust={"leadership_commitment": 0.7, "risk_tolerance": 0.6},
        architecture_trust={"cloud_maturity": 0.8, "security_posture": 0.75},
        integration_trust={"system_connectivity": 0.5, "data_quality": 0.6},
        talent_trust={"ai_literacy": 0.55, "adaptability": 0.65},
    )
    assert 0.0 <= result.overall_score <= 1.0
    assert result.trust_level in ["untrusted", "conditional", "trusted", "autonomous"]
    print(f"GSTI: {result.overall_score}, Trust: {result.trust_level}, Risk: {result.deployment_risk}")


def test_raw_calculation():
    engine = ROIEngine()
    wp = WorkflowPerformance(
        completion_rate=1.0, speed_normalized=0.85,
        escalation_frequency=1.0, human_intervention=0.8, stability=1.0,
    )
    bo = BusinessOutcome(
        time_saved_normalized=0.90, quality_improvement=0.85,
        revenue_impact_normalized=0.88, cost_savings_normalized=0.92,
    )
    result = engine.calculate_raw(agent_score_avg=0.874, workflow=wp, outcome=bo)
    assert 0.0 <= result.raw_score <= 1.0
    print(f"RAW Score: {result.raw_score} (Grade: {result.grade})")
    print(f"Components: {result.components}")


def test_rai_calculation():
    engine = ROIEngine()
    result = engine.calculate_rai(
        infrastructure_cost=5000, model_cost=2000,
        human_oversight_cost=3000, integration_cost=1500,
        revenue_generated=25000, cost_savings=15000,
        productivity_gains=10000, quality_improvements=5000,
    )
    assert result.rai_ratio > 1.0  # Should be profitable
    print(f"RAI: {result.rai_ratio}x, Payback: {result.payback_period_months} months")


def test_raia_calculation():
    engine = ROIEngine()
    agents = [
        {"agent_id": "agent-1", "output_value": 5000, "reliability": 0.95, "availability": 0.98, "cost": 100, "coordination_overhead": 20},
        {"agent_id": "agent-2", "output_value": 3000, "reliability": 0.90, "availability": 0.95, "cost": 80, "coordination_overhead": 15},
    ]
    result = engine.calculate_raia(agents)
    assert result.raia_ratio > 0
    print(f"RAIA: {result.raia_ratio}x")
    for a in result.per_agent_raia:
        print(f"  {a['agent_id']}: RAIA={a['raia']}")


def test_total_roi():
    engine = ROIEngine()
    wp = WorkflowPerformance(1.0, 0.85, 1.0, 0.8, 1.0)
    bo = BusinessOutcome(0.90, 0.85, 0.88, 0.92)
    raw_result = engine.calculate_raw(0.874, wp, bo)
    rai_result = engine.calculate_rai(5000, 2000, 3000, 1500, 25000, 15000, 10000, 5000)
    agents = [
        {"agent_id": "a1", "output_value": 5000, "reliability": 0.95, "availability": 0.98, "cost": 100, "coordination_overhead": 20},
    ]
    raia_result = engine.calculate_raia(agents)
    total = engine.calculate_total_roi(raw_result, rai_result, raia_result, coordination_tax=0.25)
    print(f"\nTotal ROI: {total.total_roi}")
    print(f"  HITL: {total.hitl_score}")
    print(f"  Agent ROI: {total.agent_roi}")
    print(f"  Synergy: {total.synergy_factor}")
    print(f"  Grade: {total.grade}")


if __name__ == "__main__":
    print("=" * 60)
    print("FuzeBox AEOS — Scoring Engine Tests")
    print("=" * 60)

    print("\n--- CAITO Basic ---")
    test_caito_basic()

    print("\n--- CAITO Simulation ---")
    test_caito_simulation()

    print("\n--- GSTI Agent Scoring ---")
    test_gsti_agent_scoring()

    print("\n--- GSTI Full ---")
    test_gsti_full()

    print("\n--- RAW Calculation ---")
    test_raw_calculation()

    print("\n--- RAI Calculation ---")
    test_rai_calculation()

    print("\n--- RAIA Calculation ---")
    test_raia_calculation()

    print("\n--- Total ROI ---")
    test_total_roi()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
