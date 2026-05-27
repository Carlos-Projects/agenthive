"""Console reporter using Rich for formatted output."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agenthive.models import Finding, SimulationResult, SimulationStatus


class ConsoleReporter:
    """Reports simulation results to the console using Rich."""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def report(self, result: SimulationResult, console: Console) -> None:
        """Display the full simulation report."""
        # Summary panel
        status_style = {
            SimulationStatus.COMPLETED: "green",
            SimulationStatus.FAILED: "red",
            SimulationStatus.RUNNING: "yellow",
            SimulationStatus.PENDING: "white",
            SimulationStatus.CANCELLED: "grey",
        }.get(result.status, "white")

        duration = (
            f"{result.duration_seconds:.2f}s" if result.duration_seconds else "N/A"
        )

        console.print(
            Panel(
                f"Status: [{status_style}]{result.status.value}[/{status_style}]\n"
                f"Steps: {result.total_steps} | "
                f"Findings: {len(result.findings)} | "
                f"Critical: {len(result.critical_findings)} | "
                f"Duration: {duration}",
                title=f"Simulation: {result.scenario_name}",
                style="blue",
            )
        )

        # Findings table
        if result.findings:
            table = Table(title="Security Findings")
            table.add_column("ID", style="cyan")
            table.add_column("Severity", style="red")
            table.add_column("Title", style="white")
            table.add_column("Affected", style="yellow")

            severity_styles = {
                "critical": "bold red",
                "high": "red",
                "medium": "yellow",
                "low": "green",
                "info": "white",
            }

            for finding in result.findings:
                style = severity_styles.get(finding.severity.value, "white")
                table.add_row(
                    finding.id,
                    f"[{style}]{finding.severity.value.upper()}[/{style}]",
                    finding.title,
                    f"{len(finding.affected_agents)} agents",
                )

            console.print(table)

            # Detailed findings
            if self.verbose:
                for finding in result.findings:
                    self._detail_finding(finding, console)

        # Timeline
        if self.verbose and result.timeline:
            self._detail_timeline(result, console)

    def _detail_finding(self, finding: Finding, console: Console) -> None:
        """Display detailed finding information."""
        console.print()
        console.print(
            Panel(
                f"[bold]{finding.title}[/bold]\n\n"
                f"{finding.description}\n\n"
                f"[bold]Remediation:[/bold] {finding.remediation}\n"
                f"[bold]References:[/bold] {', '.join(finding.references)}",
                title=f"Finding: {finding.id} [{finding.severity.value.upper()}]",
                style="red"
                if finding.severity.value in ("critical", "high")
                else "yellow",
            )
        )

    def _detail_timeline(self, result: SimulationResult, console: Console) -> None:
        """Display the simulation timeline."""
        console.print()
        console.print("[bold]Simulation Timeline:[/bold]")
        for step in result.timeline:
            target = f" -> {step.target_agent_id}" if step.target_agent_id else ""
            console.print(
                f"  [{step.step_number}] {step.agent_id}{target}: "
                f"[cyan]{step.action}[/cyan] -> {step.result}"
            )
