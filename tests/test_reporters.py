"""Tests for all reporter modules."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from rich.console import Console

from agenthive.models import (
    AttackCategory,
    Finding,
    Severity,
    SimulationResult,
    SimulationStatus,
    SimulationStep,
)
from agenthive.reporters.console import ConsoleReporter
from agenthive.reporters.html import HtmlReporter
from agenthive.reporters.json import JsonReporter
from agenthive.reporters.sarif import SarifReporter


@pytest.fixture
def sample_result() -> SimulationResult:
    result = SimulationResult(
        scenario_name="test-scenario",
        status=SimulationStatus.COMPLETED,
    )
    result.add_step(
        SimulationStep(
            step_number=1,
            agent_id="agent-1",
            action="test_action",
            result="test_result",
            target_agent_id="agent-2",
            details={"key": "value"},
        )
    )
    result.add_finding(
        Finding(
            scenario_name="test-scenario",
            attack_category=AttackCategory.TOOL_DRIFT,
            severity=Severity.CRITICAL,
            title="Critical Finding",
            description="A critical finding description",
            affected_agents=["agent-1", "agent-2"],
            remediation="Fix the issue",
            references=["https://example.com/advisory"],
            metadata={"cvss": 9.0},
        )
    )
    result.add_finding(
        Finding(
            scenario_name="test-scenario",
            attack_category=AttackCategory.CROSS_AGENT_INJECTION,
            severity=Severity.LOW,
            title="Low Finding",
            description="A low severity finding",
            affected_agents=["agent-1"],
        )
    )
    return result


class TestJsonReporter:
    def test_write_json(self, sample_result: SimulationResult, tmp_path: Path) -> None:
        reporter = JsonReporter()
        path = tmp_path / "output.json"
        reporter.write(sample_result, path)
        assert path.exists()

        with open(path) as f:
            data = json.load(f)

        assert data["scenario_name"] == "test-scenario"
        assert data["status"] == SimulationStatus.COMPLETED.value
        assert len(data["findings"]) == 2
        assert data["findings"][0]["severity"] == "critical"
        assert data["findings"][1]["severity"] == "low"
        assert len(data["timeline"]) == 1

    def test_write_json_no_findings(self, tmp_path: Path) -> None:
        result = SimulationResult(scenario_name="empty")
        reporter = JsonReporter()
        path = tmp_path / "empty.json"
        reporter.write(result, path)
        assert path.exists()

        with open(path) as f:
            data = json.load(f)

        assert data["scenario_name"] == "empty"
        assert len(data["findings"]) == 0
        assert data["total_steps"] == 0


class TestConsoleReporter:
    def test_report_non_verbose(self, sample_result: SimulationResult) -> None:
        console = Console(width=200, force_terminal=True, color_system=None)
        reporter = ConsoleReporter(verbose=False)
        # Should not raise
        reporter.report(sample_result, console)

    def test_report_verbose(self, sample_result: SimulationResult) -> None:
        console = Console(width=200, force_terminal=True, color_system=None)
        reporter = ConsoleReporter(verbose=True)
        reporter.report(sample_result, console)

    def test_report_empty(self) -> None:
        console = Console(width=200, force_terminal=True, color_system=None)
        result = SimulationResult(scenario_name="empty")
        reporter = ConsoleReporter(verbose=True)
        reporter.report(result, console)

    def test_report_failed_status(self) -> None:
        console = Console(width=200, force_terminal=True, color_system=None)
        result = SimulationResult(
            scenario_name="failed-test",
            status=SimulationStatus.FAILED,
            metadata={"error": "something broke"},
        )
        reporter = ConsoleReporter(verbose=True)
        reporter.report(result, console)

    def test_report_various_severities(self) -> None:
        console = Console(width=200, force_terminal=True, color_system=None)
        result = SimulationResult(scenario_name="severity-test")
        for sev in Severity:
            result.add_finding(
                Finding(
                    scenario_name="severity-test",
                    attack_category=AttackCategory.TOOL_DRIFT,
                    severity=sev,
                    title=f"{sev.value} finding",
                    description=f"A {sev.value} test",
                    affected_agents=["agent-1"],
                )
            )
        result.status = SimulationStatus.CANCELLED
        reporter = ConsoleReporter(verbose=True)
        reporter.report(result, console)


class TestHtmlReporter:
    def test_write_html(self, sample_result: SimulationResult, tmp_path: Path) -> None:
        reporter = HtmlReporter()
        path = tmp_path / "report.html"
        reporter.write(sample_result, path)
        assert path.exists()

        content = path.read_text()
        assert "test-scenario" in content
        assert "Critical Finding" in content
        assert "Low Finding" in content
        assert "completed" in content
        assert "CRITICAL" in content
        assert "LOW" in content

    def test_write_html_empty(self, tmp_path: Path) -> None:
        result = SimulationResult(scenario_name="empty")
        reporter = HtmlReporter()
        path = tmp_path / "empty.html"
        reporter.write(result, path)
        assert path.exists()
        content = path.read_text()
        assert "empty" in content


class TestSarifReporter:
    def test_write_sarif(self, sample_result: SimulationResult, tmp_path: Path) -> None:
        reporter = SarifReporter()
        path = tmp_path / "results.sarif"
        reporter.write(sample_result, path)
        assert path.exists()

        with open(path) as f:
            data = json.load(f)

        assert data["version"] == "2.1.0"
        assert len(data["runs"]) == 1
        run = data["runs"][0]

        # Check tool info
        driver = run["tool"]["driver"]
        assert driver["name"] == "AgentHive"
        assert driver["version"] == "0.1.0"

        # Check rules (2 categories, but only 1 unique rule per category)
        assert len(driver["rules"]) == 2

        # Check results
        assert len(run["results"]) == 2

    def test_write_sarif_empty(self, tmp_path: Path) -> None:
        result = SimulationResult(scenario_name="empty")
        reporter = SarifReporter()
        path = tmp_path / "empty.sarif"
        reporter.write(result, path)
        assert path.exists()

        with open(path) as f:
            data = json.load(f)

        run = data["runs"][0]
        assert len(run["tool"]["driver"]["rules"]) == 0
        assert len(run["results"]) == 0

    def test_sarif_duplicate_rules(self, tmp_path: Path) -> None:
        """Test that duplicate categories don't create duplicate rules."""
        result = SimulationResult(scenario_name="dedup-test")
        for i in range(3):
            result.add_finding(
                Finding(
                    scenario_name="dedup-test",
                    attack_category=AttackCategory.TOOL_DRIFT,
                    severity=Severity.HIGH,
                    title=f"Finding {i}",
                    description=f"Test finding {i}",
                    affected_agents=["a1"],
                )
            )

        reporter = SarifReporter()
        path = tmp_path / "dedup.sarif"
        reporter.write(result, path)
        assert path.exists()

        with open(path) as f:
            data = json.load(f)

        rules = data["runs"][0]["tool"]["driver"]["rules"]
        assert len(rules) == 1  # Only one unique category
        assert len(data["runs"][0]["results"]) == 3

    def test_sarif_all_severity_levels(self, tmp_path: Path) -> None:
        result = SimulationResult(scenario_name="severity-test")
        for sev in Severity:
            result.add_finding(
                Finding(
                    scenario_name="severity-test",
                    attack_category=AttackCategory.LONG_HORIZON,
                    severity=sev,
                    title=f"{sev.value} finding",
                    description=f"A {sev.value} test",
                    affected_agents=["a1"],
                )
            )

        reporter = SarifReporter()
        path = tmp_path / "severity.sarif"
        reporter.write(result, path)
        with open(path) as f:
            data = json.load(f)

        results = data["runs"][0]["results"]
        severity_to_level = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "note",
        }
        for r in results:
            finding_sev = r["message"]["text"].replace(" finding", "")
            expected_level = severity_to_level[finding_sev]
            assert (
                r["level"] == expected_level
            ), f"{finding_sev} -> {r['level']} != {expected_level}"
