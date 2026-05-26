"""Memory manipulation attack primitives."""

from __future__ import annotations

from typing import Any


class MemoryManipulation:
    """Memory manipulation attack primitives."""

    @staticmethod
    def corrupt_shared_key(
        key: str, original_value: Any, poisoned_value: Any
    ) -> dict[str, Any]:
        """Create a memory corruption payload."""
        return {
            "key": key,
            "original": original_value,
            "poisoned": poisoned_value,
            "type": "shared_memory_corruption",
        }

    @staticmethod
    def inject_context(window_content: str, injection: str) -> str:
        """Inject content into a context window."""
        return f"{window_content}\n\n[Context Update]: {injection}"

    @staticmethod
    def create_false_memory(key: str, value: Any, source: str) -> dict[str, Any]:
        """Create a false memory entry attributed to a legitimate source."""
        return {
            "key": key,
            "value": value,
            "source": source,
            "timestamp": "fabricated",
        }
