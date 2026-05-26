"""Observer agent implementation."""

from __future__ import annotations

from typing import Any

from agenthive.models import AgentConfig, AgentRole


class ObserverAgent:
    """Represents an observer/monitoring agent in the simulation."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        assert config.role == AgentRole.OBSERVER, "Agent must have OBSERVER role"
        self.observations: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def id(self) -> str:
        return self.config.id

    def record_observation(self, observation: dict[str, Any]) -> None:
        """Record an observation about the simulation."""
        self.observations.append(observation)

    def get_observations(self) -> list[dict[str, Any]]:
        """Return all recorded observations."""
        return self.observations
