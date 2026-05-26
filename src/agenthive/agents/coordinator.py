"""Coordinator agent implementation."""

from __future__ import annotations

from agenthive.models import AgentConfig, AgentRole


class CoordinatorAgent:
    """Represents a coordinator agent that manages multi-agent workflows."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        assert config.role == AgentRole.COORDINATOR, "Agent must have COORDINATOR role"
        self.managed_agents: list[str] = []

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def id(self) -> str:
        return self.config.id

    def add_managed_agent(self, agent_id: str) -> None:
        """Add an agent to the coordination list."""
        if agent_id not in self.managed_agents:
            self.managed_agents.append(agent_id)

    def get_managed_agents(self) -> list[str]:
        """Return list of managed agent IDs."""
        return self.managed_agents
