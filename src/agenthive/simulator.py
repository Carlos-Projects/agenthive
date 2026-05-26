"""Core simulation engine for multi-agent attack scenarios."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from agenthive.models import (
    AgentConfig,
    AgentRole,
    ScenarioConfig,
    SimulationResult,
    SimulationStatus,
    SimulationStep,
)

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Core engine that orchestrates multi-agent attack simulations."""

    def __init__(self) -> None:
        self._scenario_handlers: dict[str, Callable[..., Any]] = {}

    def register_handler(
        self,
        category: str,
        handler: Callable[..., Any],
    ) -> None:
        """Register a handler for a specific attack category."""
        self._scenario_handlers[category] = handler

    async def run_scenario(
        self,
        scenario: ScenarioConfig,
    ) -> SimulationResult:
        """Execute a complete simulation scenario.

        Args:
            scenario: The scenario configuration to run.

        Returns:
            SimulationResult with findings and timeline.
        """
        result = SimulationResult(
            scenario_name=scenario.name,
            status=SimulationStatus.RUNNING,
        )

        logger.info(
            "Starting simulation: %s with %d agents and %d attacks",
            scenario.name,
            len(scenario.agents),
            len(scenario.attacks),
        )

        try:
            for attack in scenario.attacks:
                if result.total_steps >= scenario.max_steps:
                    break

                handler = self._scenario_handlers.get(attack.category.value)
                if handler is None:
                    logger.warning(
                        "No handler for attack category: %s", attack.category
                    )
                    continue

                steps = await handler(scenario, attack, result)
                for step in steps:
                    if result.total_steps >= scenario.max_steps:
                        break
                    result.add_step(step)

                if result.total_steps >= scenario.max_steps:
                    break

            result.status = SimulationStatus.COMPLETED
            result.completed_at = datetime.now(UTC)

        except Exception as e:
            result.status = SimulationStatus.FAILED
            result.completed_at = datetime.now(UTC)
            result.metadata["error"] = str(e)
            logger.exception("Simulation failed: %s", e)

        return result

    async def run_step(
        self,
        agent: AgentConfig,
        target: AgentConfig | None,
        action: str,
        result: str,
        simulation: SimulationResult,
        details: dict[str, Any] | None = None,
    ) -> SimulationStep:
        """Create and record a single simulation step.

        Args:
            agent: The agent performing the action.
            target: The target agent (if any).
            action: Description of the action.
            result: Outcome of the action.
            simulation: The simulation result to append to.
            details: Additional step details.

        Returns:
            The created SimulationStep (already added to simulation).
        """

        step = SimulationStep(
            step_number=simulation.total_steps + 1,
            agent_id=agent.id,
            action=action,
            target_agent_id=target.id if target else None,
            result=result,
            details=details or {},
        )
        simulation.add_step(step)
        return step

    def get_attackers(self, scenario: ScenarioConfig) -> list[AgentConfig]:
        """Get all attacker-role agents from a scenario."""
        return [a for a in scenario.agents if a.role == AgentRole.ATTACKER]

    def get_victims(self, scenario: ScenarioConfig) -> list[AgentConfig]:
        """Get all victim-role agents from a scenario."""
        return [a for a in scenario.agents if a.role == AgentRole.VICTIM]

    def get_observers(self, scenario: ScenarioConfig) -> list[AgentConfig]:
        """Get all observer-role agents from a scenario."""
        return [a for a in scenario.agents if a.role == AgentRole.OBSERVER]


class ScenarioRunner:
    """High-level runner that manages simulation lifecycle."""

    def __init__(self, engine: SimulationEngine | None = None) -> None:
        self.engine = engine or SimulationEngine()

    async def run(
        self,
        scenario: ScenarioConfig,
    ) -> SimulationResult:
        """Run a scenario and return results."""
        return await self.engine.run_scenario(scenario)

    def register_scenario(
        self,
        category: str,
        handler: Callable[..., Any],
    ) -> None:
        """Register a scenario handler."""
        self.engine.register_handler(category, handler)
