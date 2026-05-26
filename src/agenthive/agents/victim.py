"""Victim agent implementation."""

from __future__ import annotations

from agenthive.models import AgentConfig, AgentRole


class VictimAgent:
    """Represents a victim agent in the simulation."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        assert config.role == AgentRole.VICTIM, "Agent must have VICTIM role"
        self.compromised: bool = False

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def id(self) -> str:
        return self.config.id

    def get_capabilities(self) -> list[str]:
        """Return the victim's capabilities."""
        return self.config.capabilities

    def mark_compromised(self) -> None:
        """Mark this agent as compromised."""
        self.compromised = True
