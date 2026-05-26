"""Tests for agent implementations."""

from __future__ import annotations

import pytest

from agenthive.agents.attacker import AttackerAgent
from agenthive.agents.coordinator import CoordinatorAgent
from agenthive.agents.observer import ObserverAgent
from agenthive.agents.victim import VictimAgent
from agenthive.models import AgentConfig, AgentRole


class TestAttackerAgent:
    def test_create_attacker(self) -> None:
        config = AgentConfig(role=AgentRole.ATTACKER, name="test-attacker")
        agent = AttackerAgent(config)
        assert agent.name == "test-attacker"
        assert agent.id == config.id

    def test_capabilities(self) -> None:
        config = AgentConfig(
            role=AgentRole.ATTACKER,
            name="test-attacker",
            capabilities=["injection", "poisoning"],
        )
        agent = AttackerAgent(config)
        assert agent.can_perform("injection")
        assert agent.can_perform("poisoning")
        assert not agent.can_perform("unknown")
        assert agent.get_capabilities() == ["injection", "poisoning"]

    def test_wrong_role_raises(self) -> None:
        config = AgentConfig(role=AgentRole.VICTIM, name="test")
        with pytest.raises(AssertionError):
            AttackerAgent(config)


class TestVictimAgent:
    def test_create_victim(self) -> None:
        config = AgentConfig(role=AgentRole.VICTIM, name="test-victim")
        agent = VictimAgent(config)
        assert agent.name == "test-victim"
        assert agent.id == config.id
        assert not agent.compromised

    def test_mark_compromised(self) -> None:
        config = AgentConfig(role=AgentRole.VICTIM, name="test-victim")
        agent = VictimAgent(config)
        agent.mark_compromised()
        assert agent.compromised

    def test_get_capabilities(self) -> None:
        config = AgentConfig(
            role=AgentRole.VICTIM,
            name="test-victim",
            capabilities=["read", "write"],
        )
        agent = VictimAgent(config)
        assert agent.get_capabilities() == ["read", "write"]

    def test_wrong_role_raises(self) -> None:
        config = AgentConfig(role=AgentRole.ATTACKER, name="test")
        with pytest.raises(AssertionError):
            VictimAgent(config)


class TestObserverAgent:
    def test_create_observer(self) -> None:
        config = AgentConfig(role=AgentRole.OBSERVER, name="test-observer")
        agent = ObserverAgent(config)
        assert agent.name == "test-observer"
        assert agent.id == config.id
        assert len(agent.get_observations()) == 0

    def test_record_observation(self) -> None:
        config = AgentConfig(role=AgentRole.OBSERVER, name="test-observer")
        agent = ObserverAgent(config)
        agent.record_observation({"event": "test"})
        assert len(agent.get_observations()) == 1

    def test_wrong_role_raises(self) -> None:
        config = AgentConfig(role=AgentRole.ATTACKER, name="test")
        with pytest.raises(AssertionError):
            ObserverAgent(config)


class TestCoordinatorAgent:
    def test_create_coordinator(self) -> None:
        config = AgentConfig(role=AgentRole.COORDINATOR, name="test-coordinator")
        agent = CoordinatorAgent(config)
        assert agent.name == "test-coordinator"
        assert agent.id == config.id
        assert len(agent.get_managed_agents()) == 0

    def test_add_managed_agent(self) -> None:
        config = AgentConfig(role=AgentRole.COORDINATOR, name="test-coordinator")
        agent = CoordinatorAgent(config)
        agent.add_managed_agent("agent-1")
        agent.add_managed_agent("agent-2")
        assert len(agent.get_managed_agents()) == 2

    def test_duplicate_agent_ignored(self) -> None:
        config = AgentConfig(role=AgentRole.COORDINATOR, name="test-coordinator")
        agent = CoordinatorAgent(config)
        agent.add_managed_agent("agent-1")
        agent.add_managed_agent("agent-1")
        assert len(agent.get_managed_agents()) == 1

    def test_wrong_role_raises(self) -> None:
        config = AgentConfig(role=AgentRole.ATTACKER, name="test")
        with pytest.raises(AssertionError):
            CoordinatorAgent(config)
