"""Tests for the simulation engine."""

from __future__ import annotations

from datetime import UTC

import pytest

from agenthive.models import (
    AgentConfig,
    AgentRole,
    AttackCategory,
    AttackConfig,
    Finding,
    ScenarioConfig,
    Severity,
    SimulationResult,
    SimulationStatus,
    SimulationStep,
)
from agenthive.simulator import ScenarioRunner, SimulationEngine


@pytest.fixture
def engine() -> SimulationEngine:
    return SimulationEngine()


@pytest.fixture
def runner(engine: SimulationEngine) -> ScenarioRunner:
    return ScenarioRunner(engine)


@pytest.fixture
def sample_scenario() -> ScenarioConfig:
    return ScenarioConfig(
        name="test-scenario",
        description="Test scenario",
        agents=[
            AgentConfig(role=AgentRole.ATTACKER, name="attacker-1"),
            AgentConfig(role=AgentRole.VICTIM, name="victim-1"),
            AgentConfig(role=AgentRole.VICTIM, name="victim-2"),
        ],
        attacks=[
            AttackConfig(
                category=AttackCategory.TOOL_DRIFT,
                name="Test Tool Drift",
                description="Test",
            )
        ],
    )


class TestSimulationEngine:
    def test_register_handler(self, engine: SimulationEngine) -> None:
        async def dummy_handler(
            scenario: ScenarioConfig, attack: AttackConfig, result: SimulationResult
        ) -> list[SimulationStep]:
            return []

        engine.register_handler("test", dummy_handler)
        assert "test" in engine._scenario_handlers

    def test_get_attackers(
        self, engine: SimulationEngine, sample_scenario: ScenarioConfig
    ) -> None:
        attackers = engine.get_attackers(sample_scenario)
        assert len(attackers) == 1
        assert attackers[0].role == AgentRole.ATTACKER

    def test_get_victims(
        self, engine: SimulationEngine, sample_scenario: ScenarioConfig
    ) -> None:
        victims = engine.get_victims(sample_scenario)
        assert len(victims) == 2

    def test_get_observers(
        self, engine: SimulationEngine, sample_scenario: ScenarioConfig
    ) -> None:
        observers = engine.get_observers(sample_scenario)
        assert len(observers) == 0

    def test_run_step(self, engine: SimulationEngine) -> None:
        result = SimulationResult(scenario_name="test")
        agent = AgentConfig(role=AgentRole.ATTACKER, name="attacker-1")
        target = AgentConfig(role=AgentRole.VICTIM, name="victim-1")

        import asyncio

        async def _test() -> SimulationStep:
            return await engine.run_step(
                agent, target, "test_action", "test_result", result
            )

        step = asyncio.run(_test())
        assert step.step_number == 1
        assert step.agent_id == agent.id
        assert step.target_agent_id == target.id
        assert result.total_steps == 1


class TestScenarioRunner:
    @pytest.mark.asyncio
    async def test_run_scenario(
        self, runner: ScenarioRunner, sample_scenario: ScenarioConfig
    ) -> None:
        async def dummy_handler(
            scenario: ScenarioConfig, attack: AttackConfig, result: SimulationResult
        ) -> list[SimulationStep]:
            return []

        runner.register_scenario("tool_drift", dummy_handler)
        result = await runner.run(sample_scenario)
        assert result.status == SimulationStatus.COMPLETED
        assert result.scenario_name == "test-scenario"

    @pytest.mark.asyncio
    async def test_run_scenario_no_handler(
        self, runner: ScenarioRunner, sample_scenario: ScenarioConfig
    ) -> None:
        result = await runner.run(sample_scenario)
        assert result.status == SimulationStatus.COMPLETED
        assert len(result.findings) == 0

    @pytest.mark.asyncio
    async def test_run_scenario_handler_failure(
        self, runner: ScenarioRunner, sample_scenario: ScenarioConfig
    ) -> None:
        async def failing_handler(
            scenario: ScenarioConfig, attack: AttackConfig, result: SimulationResult
        ) -> list[SimulationStep]:
            msg = "Intentional failure for testing"
            raise RuntimeError(msg)

        runner.register_scenario("tool_drift", failing_handler)
        result = await runner.run(sample_scenario)
        assert result.status == SimulationStatus.FAILED
        assert "error" in result.metadata
        assert "Intentional failure" in result.metadata["error"]


class TestSimulationResult:
    def test_add_step(self) -> None:
        result = SimulationResult(scenario_name="test")
        step = SimulationStep(step_number=1, agent_id="a1", action="test", result="ok")
        result.add_step(step)
        assert result.total_steps == 1
        assert len(result.timeline) == 1

    def test_add_finding(self) -> None:
        result = SimulationResult(scenario_name="test")
        finding = Finding(
            scenario_name="test",
            attack_category=AttackCategory.TOOL_DRIFT,
            severity=Severity.HIGH,
            title="Test Finding",
            description="Test",
            affected_agents=["a1"],
        )
        result.add_finding(finding)
        assert len(result.findings) == 1

    def test_critical_findings(self) -> None:
        result = SimulationResult(scenario_name="test")
        result.add_finding(
            Finding(
                scenario_name="test",
                attack_category=AttackCategory.TOOL_DRIFT,
                severity=Severity.CRITICAL,
                title="Critical",
                description="Test",
                affected_agents=["a1"],
            )
        )
        result.add_finding(
            Finding(
                scenario_name="test",
                attack_category=AttackCategory.TOOL_DRIFT,
                severity=Severity.LOW,
                title="Low",
                description="Test",
                affected_agents=["a1"],
            )
        )
        assert len(result.critical_findings) == 1

    def test_duration_seconds(self) -> None:
        from datetime import datetime, timedelta

        result = SimulationResult(scenario_name="test")
        result.started_at = datetime.now(UTC) - timedelta(seconds=5)
        result.completed_at = datetime.now(UTC)
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 4.0
