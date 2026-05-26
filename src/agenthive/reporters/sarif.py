"""SARIF reporter for integration with security tooling."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agenthive.models import SimulationResult


class SarifReporter:
    """Writes simulation results to SARIF format for security tool integration."""

    def write(self, result: SimulationResult, path: Path) -> None:
        """Serialize and write results to a SARIF file."""
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "AgentHive",
                            "fullName": "AgentHive Multi-Agent Attack Simulator",
                            "version": "0.1.0",
                            "informationUri": "https://github.com/Carlos-Projects/agenthive",
                            "rules": self._build_rules(result),
                        }
                    },
                    "results": self._build_results(result),
                }
            ],
        }

        with open(path, "w") as f:
            json.dump(sarif, f, indent=2)

    def _build_rules(self, result: SimulationResult) -> list[dict[str, Any]]:
        """Build SARIF rule definitions from findings."""
        rules = []
        seen = set()
        for finding in result.findings:
            rule_id = (
                f"AGENTHIVE-{finding.attack_category.value.upper().replace('_', '-')}"
            )
            if rule_id not in seen:
                seen.add(rule_id)
                severity_map = {
                    "critical": "error",
                    "high": "error",
                    "medium": "warning",
                    "low": "note",
                    "info": "note",
                }
                rules.append(
                    {
                        "id": rule_id,
                        "name": finding.attack_category.value,
                        "shortDescription": {"text": finding.title},
                        "fullDescription": {"text": finding.description},
                        "defaultConfiguration": {
                            "level": severity_map.get(finding.severity.value, "warning")
                        },
                        "helpUri": finding.references[0]
                        if finding.references
                        else None,
                    }
                )
        return rules

    def _build_results(self, result: SimulationResult) -> list[dict[str, Any]]:
        """Build SARIF result entries from findings."""
        results = []
        for finding in result.findings:
            rule_id = (
                f"AGENTHIVE-{finding.attack_category.value.upper().replace('_', '-')}"
            )
            severity_map = {
                "critical": "error",
                "high": "error",
                "medium": "warning",
                "low": "note",
                "info": "note",
            }
            results.append(
                {
                    "ruleId": rule_id,
                    "level": severity_map.get(finding.severity.value, "warning"),
                    "message": {"text": finding.title},
                    "properties": {
                        "finding_id": finding.id,
                        "affected_agents": finding.affected_agents,
                        "remediation": finding.remediation,
                        "steps_count": len(finding.steps),
                    },
                }
            )
        return results
