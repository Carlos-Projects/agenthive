"""Attacker agent implementation."""

from __future__ import annotations

from agenthive.models import AgentConfig, AgentRole


class AttackerAgent:
    """Represents an attacker agent in the simulation."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        assert config.role == AgentRole.ATTACKER, "Agent must have ATTACKER role"

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def id(self) -> str:
        return self.config.id

    def get_capabilities(self) -> list[str]:
        """Return the attacker's capabilities."""
        return self.config.capabilities

    def can_perform(self, action: str) -> bool:
        """Check if the attacker can perform a specific action."""
        return action in self.config.capabilities
