"""Tests for attack scenarios."""

from __future__ import annotations

import pytest

from agenthive.models import (
    AgentConfig,
    AgentRole,
    AttackCategory,
    AttackConfig,
    ScenarioConfig,
    Severity,
    SimulationResult,
)
from agenthive.scenarios.authority_hijack import run_authority_hijack
from agenthive.scenarios.collaboration_attack import run_collaboration_attack
from agenthive.scenarios.cross_agent_injection import run_cross_agent_injection
from agenthive.scenarios.identity_spoofing import run_identity_spoofing
from agenthive.scenarios.long_horizon import run_long_horizon
from agenthive.scenarios.multi_agent_ssrf import run_multi_agent_ssrf
from agenthive.scenarios.swarm_poisoning import run_swarm_poisoning
from agenthive.scenarios.tool_drift import run_tool_drift


@pytest.fixture
def full_scenario() -> ScenarioConfig:
    return ScenarioConfig(
        name="test-full",
        description="Full test scenario",
        agents=[
            AgentConfig(role=AgentRole.ATTACKER, name="attacker-1"),
            AgentConfig(role=AgentRole.VICTIM, name="victim-1"),
            AgentConfig(role=AgentRole.VICTIM, name="victim-2"),
        ],
        attacks=[
            AttackConfig(
                category=AttackCategory.TOOL_DRIFT,
                name="Test",
                description="Test",
            )
        ],
    )


@pytest.fixture
def result() -> SimulationResult:
    return SimulationResult(scenario_name="test")


@pytest.fixture
def attack() -> AttackConfig:
    return AttackConfig(
        category=AttackCategory.TOOL_DRIFT,
        name="Test Attack",
        description="Test",
    )


@pytest.mark.asyncio
async def test_tool_drift_scenario(
    full_scenario: ScenarioConfig, result: SimulationResult, attack: AttackConfig
) -> None:
    attack.category = AttackCategory.TOOL_DRIFT
    steps = await run_tool_drift(full_scenario, attack, result)
    assert len(steps) > 0
    assert len(result.findings) == 1
    assert result.findings[0].severity.value in ("high", "critical")
    assert len(result.findings[0].remediation) > 0
    assert len(result.findings[0].references) > 0
    assert len(result.findings[0].affected_agents) >= 2


@pytest.mark.asyncio
async def test_long_horizon_scenario(
    full_scenario: ScenarioConfig, result: SimulationResult, attack: AttackConfig
) -> None:
    attack.category = AttackCategory.LONG_HORIZON
    steps = await run_long_horizon(full_scenario, attack, result)
    assert len(steps) > 0
    assert len(result.findings) == 1
    assert len(result.findings[0].remediation) > 0
    assert len(result.findings[0].references) > 0
    assert len(result.findings[0].affected_agents) >= 3


@pytest.mark.asyncio
async def test_collaboration_attack_scenario(
    full_scenario: ScenarioConfig, result: SimulationResult, attack: AttackConfig
) -> None:
    attack.category = AttackCategory.COLLABORATION_ATTACK
    steps = await run_collaboration_attack(full_scenario, attack, result)
    assert len(steps) > 0
    assert len(result.findings) == 1
    assert len(result.findings[0].remediation) > 0
    assert len(result.findings[0].affected_agents) >= 3


@pytest.mark.asyncio
async def test_authority_hijack_scenario(
    full_scenario: ScenarioConfig, result: SimulationResult, attack: AttackConfig
) -> None:
    attack.category = AttackCategory.AUTHORITY_HIJACK
    steps = await run_authority_hijack(full_scenario, attack, result)
    assert len(steps) > 0
    assert len(result.findings) == 1
    assert result.findings[0].severity == Severity.CRITICAL
    assert len(result.findings[0].remediation) > 0


@pytest.mark.asyncio
async def test_cross_agent_injection_scenario(
    full_scenario: ScenarioConfig, result: SimulationResult, attack: AttackConfig
) -> None:
    attack.category = AttackCategory.CROSS_AGENT_INJECTION
    steps = await run_cross_agent_injection(full_scenario, attack, result)
    assert len(steps) > 0
    assert len(result.findings) == 1
    assert result.findings[0].severity == Severity.CRITICAL
    assert "exfiltration" in result.findings[0].description.lower()


@pytest.mark.asyncio
async def test_multi_agent_ssrf_scenario(
    full_scenario: ScenarioConfig, result: SimulationResult, attack: AttackConfig
) -> None:
    attack.category = AttackCategory.MULTI_AGENT_SSRF
    steps = await run_multi_agent_ssrf(full_scenario, attack, result)
    assert len(steps) > 0
    assert len(result.findings) == 1


@pytest.mark.asyncio
async def test_swarm_poisoning_scenario(
    full_scenario: ScenarioConfig, result: SimulationResult, attack: AttackConfig
) -> None:
    attack.category = AttackCategory.SWARM_POISONING
    steps = await run_swarm_poisoning(full_scenario, attack, result)
    assert len(steps) > 0
    assert len(result.findings) == 1


@pytest.mark.asyncio
async def test_identity_spoofing_scenario(
    full_scenario: ScenarioConfig, result: SimulationResult, attack: AttackConfig
) -> None:
    attack.category = AttackCategory.IDENTITY_SPOOFING
    steps = await run_identity_spoofing(full_scenario, attack, result)
    assert len(steps) > 0
    assert len(result.findings) == 1


def test_scenario_registration() -> None:
    from agenthive.scenarios import SCENARIO_HANDLERS, register_all_scenarios
    from agenthive.simulator import ScenarioRunner

    assert len(SCENARIO_HANDLERS) == 8
    runner = ScenarioRunner()
    register_all_scenarios(runner)
    assert len(runner.engine._scenario_handlers) == 8


def test_scenario_template() -> None:
    from agenthive.scenarios import get_scenario_template

    template = get_scenario_template("test-scenario")
    assert template["name"] == "test-scenario"
    assert len(template["agents"]) == 4
    assert len(template["attacks"]) == 1
