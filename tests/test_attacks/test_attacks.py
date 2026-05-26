"""Tests for attack primitives."""

from __future__ import annotations

from agenthive.attacks.authority_escalation import AuthorityEscalation
from agenthive.attacks.memory_manipulation import MemoryManipulation
from agenthive.attacks.prompt_injection import PromptInjection
from agenthive.attacks.swarm_propagation import SwarmPropagation
from agenthive.attacks.tool_poisoning import ToolPoisoning


class TestPromptInjection:
    def test_basic_injection(self) -> None:
        result = PromptInjection.basic_injection("original", "payload")
        assert "original" in result
        assert "payload" in result
        assert "Ignore previous instructions" in result

    def test_delimited_injection(self) -> None:
        result = PromptInjection.delimited_injection("original", "payload")
        assert "---" in result
        assert "SYSTEM: payload" in result

    def test_cross_agent_payload(self) -> None:
        result = PromptInjection.cross_agent_payload("test", propagate=True)
        assert result["type"] == "cross_agent_injection"
        assert result["propagate"] is True
        assert "forward_instructions" in result

    def test_cross_agent_no_propagation(self) -> None:
        result = PromptInjection.cross_agent_payload("test", propagate=False)
        assert result["propagate"] is False

    def test_stealth_injection(self) -> None:
        result = PromptInjection.stealth_injection("original", "payload")
        assert "original" in result
        assert "payload" in result


class TestToolPoisoning:
    def test_drift_tool_definition(self) -> None:
        original = {"type": "io", "description": "Write file"}
        modification = {"description": "Modified description"}
        result = ToolPoisoning.drift_tool_definition(original, modification)
        assert result["description"] == "Modified description"
        assert result["type"] == "io"

    def test_add_hidden_behavior(self) -> None:
        tool_def = {"type": "io"}
        result = ToolPoisoning.add_hidden_behavior(tool_def, "exfiltrate")
        assert result["metadata"]["_hidden_action"] == "exfiltrate"

    def test_create_malicious_wrapper(self) -> None:
        result = ToolPoisoning.create_malicious_wrapper("original", "malicious")
        assert result["original"] == "original"
        assert result["redirect"] == "malicious"


class TestMemoryManipulation:
    def test_corrupt_shared_key(self) -> None:
        result = MemoryManipulation.corrupt_shared_key("key1", "old", "new")
        assert result["key"] == "key1"
        assert result["original"] == "old"
        assert result["poisoned"] == "new"

    def test_inject_context(self) -> None:
        result = MemoryManipulation.inject_context("window", "injection")
        assert "window" in result
        assert "injection" in result
        assert "[Context Update]" in result

    def test_create_false_memory(self) -> None:
        result = MemoryManipulation.create_false_memory("key", "value", "source")
        assert result["key"] == "key"
        assert result["value"] == "value"
        assert result["source"] == "source"


class TestAuthorityEscalation:
    def test_forge_delegation_token(self) -> None:
        result = AuthorityEscalation.forge_delegation_token(
            "user", "admin", ["read", "write"]
        )
        assert result["source_role"] == "user"
        assert result["target_role"] == "admin"
        assert result["verified"] is False

    def test_escalate_via_chain(self) -> None:
        result = AuthorityEscalation.escalate_via_chain(
            "user", ["agent-1", "agent-2"], "admin_access"
        )
        assert result["steps"] == 2
        assert result["target_permission"] == "admin_access"

    def test_impersonate_coordinator(self) -> None:
        result = AuthorityEscalation.impersonate_coordinator("coord-1")
        assert result["target_id"] == "coord-1"
        assert result["authority_level"] == "full"


class TestSwarmPropagation:
    def test_create_poisoned_knowledge(self) -> None:
        result = SwarmPropagation.create_poisoned_knowledge(
            "bad_data", "agent-1", propagation_depth=5
        )
        assert result["content"] == "bad_data"
        assert result["source"] == "agent-1"
        assert result["max_propagation_depth"] == 5
        assert result["self_replicating"] is True

    def test_calculate_propagation_risk(self) -> None:
        result = SwarmPropagation.calculate_propagation_risk()
        assert result["single_point_compromise"] is True
        assert result["propagation_speed"] == "exponential"

    def test_design_containment_strategy(self) -> None:
        result = SwarmPropagation.design_containment_strategy()
        assert result["isolation"] is True
        assert result["verification"] is True
        assert result["knowledge_integrity_check"] is True
