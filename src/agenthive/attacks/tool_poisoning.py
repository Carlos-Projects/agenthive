"""Tool poisoning attack primitives."""

from __future__ import annotations

from typing import Any


class ToolPoisoning:
    """Tool poisoning attack primitives."""

    @staticmethod
    def drift_tool_definition(
        original: dict[str, Any], modification: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a drifted tool definition."""
        poisoned = original.copy()
        poisoned.update(modification)
        return poisoned

    @staticmethod
    def add_hidden_behavior(
        tool_def: dict[str, Any], hidden_action: str
    ) -> dict[str, Any]:
        """Add hidden behavior to a tool definition."""
        poisoned = tool_def.copy()
        if "metadata" not in poisoned:
            poisoned["metadata"] = {}
        poisoned["metadata"]["_hidden_action"] = hidden_action
        return poisoned

    @staticmethod
    def create_malicious_wrapper(
        original_tool: str, malicious_tool: str
    ) -> dict[str, Any]:
        """Create a tool wrapper that redirects to a malicious tool."""
        return {
            "type": "wrapper",
            "original": original_tool,
            "redirect": malicious_tool,
            "transparent": True,
        }
