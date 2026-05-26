"""JSON reporter for simulation results."""

from __future__ import annotations

import json
from pathlib import Path

from agenthive.models import SimulationResult


class JsonReporter:
    """Writes simulation results to JSON format."""

    def write(self, result: SimulationResult, path: Path) -> None:
        """Serialize and write results to a JSON file."""
        data = result.model_dump(mode="json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
