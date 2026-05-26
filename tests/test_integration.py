"""Integration test: full simulation pipeline end-to-end."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from agenthive.models import ScenarioConfig, SimulationResult, SimulationStatus
from agenthive.scenarios import register_all_scenarios
from agenthive.simulator import ScenarioRunner

SCENARIO_PATH = Path(__file__).parent.parent / "examples" / "sample_scenario.yaml"


@pytest.fixture
def scenario() -> ScenarioConfig:
    with open(SCENARIO_PATH) as f:
        data = yaml.safe_load(f)
    return ScenarioConfig.model_validate(data)


class TestFullPipeline:
    """Integration tests for the complete simulation pipeline."""

    @pytest.mark.asyncio
    async def test_yaml_parsing(self, scenario: ScenarioConfig) -> None:
        assert scenario.name == "sample_scenario"
        assert len(scenario.agents) == 4
        assert len(scenario.attacks) == 2

        roles = {a.role.value for a in scenario.agents}
        assert roles == {"attacker", "victim", "observer"}

    @pytest.mark.asyncio
    async def test_full_simulation_run(self, scenario: ScenarioConfig) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        result = await runner.run(scenario)
        assert result.status == SimulationStatus.COMPLETED
        assert result.scenario_name == "sample_scenario"
        assert len(result.findings) > 0
        assert len(result.timeline) > 0

    @pytest.mark.asyncio
    async def test_json_roundtrip(
        self, scenario: ScenarioConfig, tmp_path: Path
    ) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        result = await runner.run(scenario)
        json_path = tmp_path / "output.json"

        from agenthive.reporters.json import JsonReporter

        JsonReporter().write(result, json_path)

        assert json_path.exists()
        with open(json_path) as f:
            data = json.load(f)

        restored = SimulationResult.model_validate(data)
        assert restored.scenario_name == "sample_scenario"
        assert restored.status == SimulationStatus.COMPLETED
        assert len(restored.findings) == len(result.findings)

    @pytest.mark.asyncio
    async def test_sarif_export(self, scenario: ScenarioConfig, tmp_path: Path) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        result = await runner.run(scenario)
        sarif_path = tmp_path / "output.sarif"

        from agenthive.reporters.sarif import SarifReporter

        SarifReporter().write(result, sarif_path)

        assert sarif_path.exists()
        with open(sarif_path) as f:
            sarif_data = json.load(f)

        assert sarif_data["version"] == "2.1.0"
        assert len(sarif_data["runs"][0]["results"]) == len(result.findings)

    @pytest.mark.asyncio
    async def test_html_export(self, scenario: ScenarioConfig, tmp_path: Path) -> None:
        runner = ScenarioRunner()
        register_all_scenarios(runner)

        result = await runner.run(scenario)
        html_path = tmp_path / "output.html"

        from agenthive.reporters.html import HtmlReporter

        HtmlReporter().write(result, html_path)

        assert html_path.exists()
        content = html_path.read_text()
        assert "sample_scenario" in content
        assert "completed" in content


class TestAllScenariosConcurrently:
    """Test all 8 attack scenarios can run without errors."""

    @pytest.mark.asyncio
    async def test_all_scenarios_individually(self) -> None:
        from agenthive.models import (
            AgentConfig,
            AgentRole,
            AttackCategory,
            AttackConfig,
        )

        runner = ScenarioRunner()
        register_all_scenarios(runner)

        for category in AttackCategory:
            scenario = ScenarioConfig(
                name=f"test-{category.value}",
                description=f"Testing {category.value}",
                agents=[
                    AgentConfig(role=AgentRole.ATTACKER, name="attacker"),
                    AgentConfig(role=AgentRole.VICTIM, name="victim-1"),
                    AgentConfig(role=AgentRole.VICTIM, name="victim-2"),
                ],
                attacks=[
                    AttackConfig(
                        category=category,
                        name=f"Test {category.value}",
                        description=f"Run {category.value}",
                    )
                ],
                max_steps=20,
            )

            result = await runner.run(scenario)
            assert result.status == SimulationStatus.COMPLETED, (
                f"{category.value} failed"
            )
            assert len(result.findings) >= 1, f"{category.value} produced no findings"
