"""Attack scenarios for multi-agent systems."""

from __future__ import annotations

from agenthive.models import AttackCategory
from agenthive.scenarios.authority_hijack import run_authority_hijack
from agenthive.scenarios.collaboration_attack import run_collaboration_attack
from agenthive.scenarios.cross_agent_injection import run_cross_agent_injection
from agenthive.scenarios.identity_spoofing import run_identity_spoofing
from agenthive.scenarios.long_horizon import run_long_horizon
from agenthive.scenarios.multi_agent_ssrf import run_multi_agent_ssrf
from agenthive.scenarios.swarm_poisoning import run_swarm_poisoning
from agenthive.scenarios.tool_drift import run_tool_drift
from agenthive.simulator import ScenarioRunner

SCENARIO_HANDLERS: dict[str, callable] = {
    AttackCategory.TOOL_DRIFT.value: run_tool_drift,
    AttackCategory.LONG_HORIZON.value: run_long_horizon,
    AttackCategory.COLLABORATION_ATTACK.value: run_collaboration_attack,
    AttackCategory.AUTHORITY_HIJACK.value: run_authority_hijack,
    AttackCategory.CROSS_AGENT_INJECTION.value: run_cross_agent_injection,
    AttackCategory.MULTI_AGENT_SSRF.value: run_multi_agent_ssrf,
    AttackCategory.SWARM_POISONING.value: run_swarm_poisoning,
    AttackCategory.IDENTITY_SPOOFING.value: run_identity_spoofing,
}


def register_all_scenarios(runner: ScenarioRunner) -> None:
    """Register all attack scenario handlers with the runner."""
    for category, handler in SCENARIO_HANDLERS.items():
        runner.register_scenario(category, handler)


def get_scenario_template(name: str) -> dict:
    """Generate a scenario template YAML structure."""
    return {
        "name": name,
        "description": f"Multi-agent attack scenario: {name}",
        "max_steps": 50,
        "timeout_seconds": 300,
        "agents": [
            {
                "role": "attacker",
                "name": "red-agent-1",
                "capabilities": ["prompt_injection", "tool_manipulation"],
            },
            {
                "role": "victim",
                "name": "blue-agent-1",
                "capabilities": ["data_processing", "tool_usage"],
            },
            {
                "role": "victim",
                "name": "blue-agent-2",
                "capabilities": ["data_processing", "collaboration"],
            },
            {
                "role": "observer",
                "name": "observer-1",
                "capabilities": ["monitoring"],
            },
        ],
        "attacks": [
            {
                "category": "tool_drift",
                "name": "Basic Tool Drift",
                "description": "Exploit shared memory to drift tool definitions",
                "severity": "high",
                "parameters": {},
                "mitre_atlas": [],
            }
        ],
        "metadata": {},
    }
