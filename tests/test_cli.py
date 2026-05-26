"""Smoke tests for the main CLI entry point."""

from __future__ import annotations

from typer.testing import CliRunner


class TestMainCLI:
    """Smoke tests for all CLI commands."""

    def test_help(self) -> None:
        from agenthive.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Multi-agent attack simulation framework" in result.output
        assert "simulate" in result.output
        assert "scenario" in result.output
        assert "report" in result.output
        assert "lab" in result.output
        assert "list-scenarios" in result.output

    def test_list_scenarios(self) -> None:
        from agenthive.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["list-scenarios"])
        assert result.exit_code == 0
        assert "Available Attack Scenarios" in result.output
        assert "tool_drift" in result.output
        assert "long_horizon" in result.output
        assert "collaboration_attack" in result.output
        assert "swarm_poisoning" in result.output
        assert "identity_spoofing" in result.output

    def test_scenario_help(self) -> None:
        from agenthive.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["scenario", "--help"])
        assert result.exit_code == 0
        assert "Generate a scenario template" in result.output

    def test_simulate_help(self) -> None:
        from agenthive.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "Run a multi-agent attack simulation" in result.output

    def test_report_help(self) -> None:
        from agenthive.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0
        assert "Display or convert simulation results" in result.output

    def test_lab_help(self) -> None:
        from agenthive.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["lab", "--help"])
        assert result.exit_code == 0
        assert "Start the vulnerable multi-agent lab server" in result.output
