"""Additional edge case and integration tests."""

from __future__ import annotations

import pytest

from agenthive.models import (
    AgentConfig,
    AgentRole,
    AttackCategory,
    AttackConfig,
    ScenarioConfig,
    Severity,
    SimulationStatus,
)
from agenthive.simulator import ScenarioRunner, SimulationEngine


class TestAgentConfig:
    def test_default_id_generated(self) -> None:
        config = AgentConfig(role=AgentRole.ATTACKER, name="test")
        assert len(config.id) == 8

    def test_unique_ids(self) -> None:
        a = AgentConfig(role=AgentRole.ATTACKER, name="test1")
        b = AgentConfig(role=AgentRole.ATTACKER, name="test2")
        assert a.id != b.id

    def test_all_roles_configurable(self) -> None:
        for role in AgentRole:
            config = AgentConfig(role=role, name=f"agent-{role}")
            assert config.role == role


class TestAttackConfig:
    def test_default_severity(self) -> None:
        config = AttackConfig(
            category=AttackCategory.TOOL_DRIFT,
            name="test",
            description="test",
        )
        assert config.severity == Severity.MEDIUM

    def test_all_categories(self) -> None:
        for cat in AttackCategory:
            config = AttackConfig(
                category=cat,
                name=cat.value,
                description=f"Test {cat.value}",
            )
            assert config.category == cat

    def test_mitre_atlas_empty_by_default(self) -> None:
        config = AttackConfig(
            category=AttackCategory.TOOL_DRIFT,
            name="test",
            description="test",
        )
        assert config.mitre_atlas == []


class TestScenarioConfig:
    def test_default_max_steps(self) -> None:
        scenario = ScenarioConfig(
            name="test",
            description="test",
            agents=[AgentConfig(role=AgentRole.ATTACKER, name="a")],
            attacks=[
                AttackConfig(
                    category=AttackCategory.TOOL_DRIFT,
                    name="t",
                    description="t",
                )
            ],
        )
        assert scenario.max_steps == 50
        assert scenario.timeout_seconds == 300

    def test_minimal_scenario(self) -> None:
        scenario = ScenarioConfig(
            name="minimal",
            description="minimal scenario",
            agents=[],
            attacks=[],
        )
        assert len(scenario.agents) == 0
        assert len(scenario.attacks) == 0

    def test_metadata_defaults(self) -> None:
        scenario = ScenarioConfig(
            name="test", description="test", agents=[], attacks=[]
        )
        assert scenario.metadata == {}


class TestModelSerialization:
    def test_scenario_config_yaml_roundtrip(self) -> None:
        import yaml

        config = AttackConfig(
            category=AttackCategory.SWARM_POISONING,
            name="swarm test",
            description="test swarm poisoning",
            severity=Severity.CRITICAL,
            parameters={"depth": 5},
            mitre_atlas=["ATLAS-001"],
        )
        data = config.model_dump(mode="json")
        assert data["category"] == "swarm_poisoning"
        assert data["severity"] == "critical"
        assert data["parameters"]["depth"] == 5

        # Round-trip through YAML
        yaml_str = yaml.dump(data, default_flow_style=False)
        loaded = yaml.safe_load(yaml_str)
        restored = AttackConfig.model_validate(loaded)
        assert restored.category == AttackCategory.SWARM_POISONING
        assert restored.severity == Severity.CRITICAL
        assert restored.parameters == {"depth": 5}

    def test_agent_config_metadata(self) -> None:
        config = AgentConfig(
            role=AgentRole.COORDINATOR,
            name="coordinator",
            mcp_url="http://mcp.local:8000",
            capabilities=["delegate", "monitor"],
            metadata={"version": "1.0", "team": "alpha"},
        )
        assert config.mcp_url == "http://mcp.local:8000"
        assert len(config.capabilities) == 2
        assert config.metadata["team"] == "alpha"


class TestSimulationStatus:
    def test_all_statuses(self) -> None:
        assert SimulationStatus.PENDING.value == "pending"
        assert SimulationStatus.RUNNING.value == "running"
        assert SimulationStatus.COMPLETED.value == "completed"
        assert SimulationStatus.FAILED.value == "failed"
        assert SimulationStatus.CANCELLED.value == "cancelled"


class TestSeverity:
    def test_all_severities(self) -> None:
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"


class TestSimulationEngineEdgeCases:
    def test_get_observers(self) -> None:
        engine = SimulationEngine()
        scenario = ScenarioConfig(
            name="test",
            description="test",
            agents=[
                AgentConfig(role=AgentRole.OBSERVER, name="obs-1"),
                AgentConfig(role=AgentRole.OBSERVER, name="obs-2"),
                AgentConfig(role=AgentRole.ATTACKER, name="att-1"),
            ],
            attacks=[],
        )
        observers = engine.get_observers(scenario)
        assert len(observers) == 2

    def test_get_attackers_empty(self) -> None:
        engine = SimulationEngine()
        scenario = ScenarioConfig(
            name="test",
            description="test",
            agents=[
                AgentConfig(role=AgentRole.VICTIM, name="v-1"),
            ],
            attacks=[],
        )
        assert engine.get_attackers(scenario) == []

    def test_get_victims_empty(self) -> None:
        engine = SimulationEngine()
        scenario = ScenarioConfig(
            name="test",
            description="test",
            agents=[AgentConfig(role=AgentRole.ATTACKER, name="a-1")],
            attacks=[],
        )
        assert engine.get_victims(scenario) == []


class TestScenarioRunnerEdgeCases:
    @pytest.mark.asyncio
    async def test_run_with_max_steps(self) -> None:
        runner = ScenarioRunner()

        async def short_handler(
            scenario: ScenarioConfig,
            attack: AttackConfig,
            result,
        ) -> list:
            from agenthive.models import SimulationStep

            steps = []
            for i in range(3):
                steps.append(
                    SimulationStep(
                        step_number=i + 1,
                        agent_id="attacker-1",
                        action=f"step_{i}",
                        result=f"result_{i}",
                    )
                )
            return steps

        runner.register_scenario("tool_drift", short_handler)

        scenario = ScenarioConfig(
            name="max-steps-test",
            description="test",
            agents=[AgentConfig(role=AgentRole.ATTACKER, name="a")],
            attacks=[
                AttackConfig(
                    category=AttackCategory.TOOL_DRIFT,
                    name="test",
                    description="test",
                )
            ],
            max_steps=5,
        )
        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_run_scenario_no_attackers(self) -> None:
        runner = ScenarioRunner()
        scenario = ScenarioConfig(
            name="no-attackers",
            description="test",
            agents=[AgentConfig(role=AgentRole.VICTIM, name="v")],
            attacks=[
                AttackConfig(
                    category=AttackCategory.TOOL_DRIFT,
                    name="t",
                    description="t",
                )
            ],
        )
        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_run_scenario_no_victims(self) -> None:
        runner = ScenarioRunner()
        scenario = ScenarioConfig(
            name="no-victims",
            description="test",
            agents=[AgentConfig(role=AgentRole.ATTACKER, name="a")],
            attacks=[
                AttackConfig(
                    category=AttackCategory.LONG_HORIZON,
                    name="t",
                    description="t",
                )
            ],
        )
        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED


class TestCLIImports:
    def test_cli_module_imports(self) -> None:
        from agenthive import cli

        assert hasattr(cli, "app")
        assert callable(cli.app)

    def test_cli_has_commands(self) -> None:
        from agenthive.cli import app

        commands = list(app.registered_commands)
        assert len(commands) > 0


class TestMainModule:
    """Test the __main__.py entry point."""

    def test_main_imports_and_has_app(self) -> None:
        from agenthive import __main__
        from agenthive.cli import app

        assert __main__.app is app

    def test_package_direct_execution(self) -> None:
        import runpy
        import sys

        sys_argv = sys.argv
        try:
            sys.argv = ["agenthive", "--help"]
            runpy.run_module("agenthive", run_name="__main__", alter_sys=True)
        except SystemExit:
            pass
        finally:
            sys.argv = sys_argv
