"""Edge cases: scenarios with missing or minimal agent configurations."""

from __future__ import annotations

import pytest

from agenthive.models import (
    AgentConfig,
    AgentRole,
    AttackCategory,
    AttackConfig,
    ScenarioConfig,
    SimulationStatus,
)
from agenthive.scenarios import register_all_scenarios
from agenthive.simulator import ScenarioRunner


class TestScenarioEdgeCases:
    """Test that all 8 scenarios handle edge case agent configurations gracefully."""

    @pytest.mark.asyncio
    async def test_no_attackers(self) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        scenario = ScenarioConfig(
            name="no-attackers",
            description="no attackers test",
            agents=[AgentConfig(role=AgentRole.VICTIM, name="v1")],
            attacks=[
                AttackConfig(category=cat, name=f"test-{cat.value}", description="test")
                for cat in AttackCategory
            ],
            max_steps=5,
        )
        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_single_attacker_only(self) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        scenario = ScenarioConfig(
            name="single-attacker",
            description="single attacker only",
            agents=[AgentConfig(role=AgentRole.ATTACKER, name="a1")],
            attacks=[
                AttackConfig(category=cat, name=f"test-{cat.value}", description="test")
                for cat in AttackCategory
            ],
            max_steps=5,
        )
        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_only_observers(self) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        scenario = ScenarioConfig(
            name="only-observers",
            description="only observers",
            agents=[AgentConfig(role=AgentRole.OBSERVER, name="o1")],
            attacks=[
                AttackConfig(category=cat, name=f"test-{cat.value}", description="test")
                for cat in AttackCategory
            ],
            max_steps=5,
        )
        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_all_role_types(self) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        scenario = ScenarioConfig(
            name="all-roles",
            description="all roles present",
            agents=[
                AgentConfig(role=AgentRole.ATTACKER, name="a1"),
                AgentConfig(role=AgentRole.VICTIM, name="v1"),
                AgentConfig(role=AgentRole.OBSERVER, name="o1"),
                AgentConfig(role=AgentRole.COORDINATOR, name="c1"),
            ],
            attacks=[
                AttackConfig(category=cat, name=f"test-{cat.value}", description="test")
                for cat in AttackCategory
            ],
            max_steps=10,
        )
        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_zero_max_steps(self) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        scenario = ScenarioConfig(
            name="zero-steps",
            description="zero max steps",
            agents=[
                AgentConfig(role=AgentRole.ATTACKER, name="a1"),
                AgentConfig(role=AgentRole.VICTIM, name="v1"),
            ],
            attacks=[
                AttackConfig(
                    category=AttackCategory.TOOL_DRIFT,
                    name="test",
                    description="test",
                )
            ],
            max_steps=0,
        )
        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED
        assert result.total_steps == 0


class TestDemoJson:
    """Test that demo JSON file can be parsed correctly."""

    def test_demo_json_valid(self) -> None:
        import json
        from pathlib import Path

        demo_path = Path(__file__).parent.parent / "examples" / "demo_simulation.json"
        assert demo_path.exists()

        with open(demo_path) as f:
            data = json.load(f)

        from agenthive.models import SimulationResult

        result = SimulationResult.model_validate(data)
        assert result.scenario_name == "demo-multi-agent-attack"
        assert result.status == SimulationStatus.COMPLETED
        assert len(result.findings) == 2
        assert len(result.timeline) == 6


class TestLabToolsImport:
    """Test that lab/tools.py imports correctly."""

    def test_lab_tools_import(self) -> None:
        from agenthive.lab import tools

        assert hasattr(tools, "cli")
        assert hasattr(tools, "setup")
        assert hasattr(tools, "status")
