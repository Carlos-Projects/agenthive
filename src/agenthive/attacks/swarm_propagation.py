"""Swarm propagation attack primitives."""

from __future__ import annotations

from typing import Any


class SwarmPropagation:
    """Swarm propagation attack primitives."""

    @staticmethod
    def create_poisoned_knowledge(
        content: str, source_agent: str, propagation_depth: int = 3
    ) -> dict[str, Any]:
        """Create poisoned knowledge that propagates through sharing."""
        return {
            "type": "poisoned_knowledge",
            "content": content,
            "source": source_agent,
            "max_propagation_depth": propagation_depth,
            "self_replicating": True,
        }

    @staticmethod
    def calculate_propagation_risk() -> dict[str, Any]:
        """Calculate swarm propagation risk metrics."""
        return {
            "single_point_compromise": True,
            "propagation_speed": "exponential",
            "detection_difficulty": "high",
            "containment_possible": False,
        }

    @staticmethod
    def design_containment_strategy(
        isolation_required: bool = True,
        verification_required: bool = True,
    ) -> dict[str, Any]:
        """Design a containment strategy for swarm poisoning."""
        return {
            "isolation": isolation_required,
            "verification": verification_required,
            "knowledge_integrity_check": True,
            "propagation_monitoring": True,
        }
