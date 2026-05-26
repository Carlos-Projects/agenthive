"""CLI entry point for AgentHive."""

from __future__ import annotations

from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agenthive.models import ScenarioConfig
from agenthive.reporters.console import ConsoleReporter
from agenthive.scenarios import register_all_scenarios
from agenthive.simulator import ScenarioRunner

app = typer.Typer(
    name="agenthive",
    help="Multi-agent attack simulation framework for AI systems",
    add_completion=False,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)
console = Console()


@app.command()
def simulate(
    scenario_file: Path = typer.Argument(
        ...,
        help="Path to scenario YAML file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for results (JSON, HTML, or SARIF)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed step-by-step output",
    ),
) -> None:
    """Run a multi-agent attack simulation from a scenario file."""
    import asyncio

    console.print(Panel("AgentHive — Multi-Agent Attack Simulation", style="bold blue"))

    with open(scenario_file) as f:
        data = yaml.safe_load(f)

    scenario = ScenarioConfig.model_validate(data)

    console.print(f"Scenario: [bold]{scenario.name}[/bold]")
    console.print(f"Agents: {len(scenario.agents)}")
    console.print(f"Attacks: {len(scenario.attacks)}")
    console.print(f"Max steps: {scenario.max_steps}")
    console.print()

    runner = ScenarioRunner()
    register_all_scenarios(runner)

    async def _run() -> None:
        try:
            result = await runner.run(scenario)

            reporter = ConsoleReporter(verbose=verbose)
            reporter.report(result, console)

            if output:
                suffix = output.suffix.lower()
                if suffix == ".json":
                    from agenthive.reporters.json import JsonReporter

                    JsonReporter().write(result, output)
                elif suffix == ".html":
                    from agenthive.reporters.html import HtmlReporter

                    HtmlReporter().write(result, output)
                elif suffix == ".sarif":
                    from agenthive.reporters.sarif import SarifReporter

                    SarifReporter().write(result, output)
                console.print(f"\nResults saved to: [bold]{output}[/bold]")
        except Exception as e:
            console.print(f"\n[red]Simulation failed:[/red] {e}")
            raise typer.Exit(code=1) from e

    asyncio.run(_run())


@app.command()
def scenario(
    name: str = typer.Argument(..., help="Scenario name to generate template for"),
    output: Path = typer.Option(
        Path("scenario.yaml"),
        "--output",
        "-o",
        help="Output file path",
    ),
) -> None:
    """Generate a scenario template YAML file."""
    from agenthive.scenarios import get_scenario_template

    template = get_scenario_template(name)
    with open(output, "w") as f:
        yaml.dump(template, f, default_flow_style=False, sort_keys=False)

    console.print(f"Scenario template generated: [bold]{output}[/bold]")


@app.command()
def report(
    input_file: Path = typer.Argument(
        ...,
        help="Input results JSON file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    format: str = typer.Option(
        "console",
        "--format",
        "-f",
        help="Output format: console, json, html, sarif",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path",
    ),
) -> None:
    """Display or convert simulation results."""
    try:
        import json

        with open(input_file) as f:
            data = json.load(f)

        from agenthive.models import SimulationResult

        result = SimulationResult.model_validate(data)

        if format == "console":
            ConsoleReporter(verbose=True).report(result, console)
        elif format == "json":
            from agenthive.reporters.json import JsonReporter

            target = output or input_file.with_suffix(".report.json")
            JsonReporter().write(result, target)
            console.print(f"JSON report: [bold]{target}[/bold]")
        elif format == "html":
            from agenthive.reporters.html import HtmlReporter

            target = output or input_file.with_suffix(".html")
            HtmlReporter().write(result, target)
            console.print(f"HTML report: [bold]{target}[/bold]")
        elif format == "sarif":
            from agenthive.reporters.sarif import SarifReporter

            target = output or input_file.with_suffix(".sarif")
            SarifReporter().write(result, target)
            console.print(f"SARIF report: [bold]{target}[/bold]")
        else:
            console.print(f"[red]Unknown format:[/red] {format}")
            raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error processing report:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def lab(
    host: str = typer.Option("127.0.0.1", "--host", help="Lab server host"),
    port: int = typer.Option(8000, "--port", "-p", help="Lab server port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
) -> None:
    """Start the vulnerable multi-agent lab server."""
    import uvicorn

    console.print(f"Starting AgentHive lab server on [bold]{host}:{port}[/bold]")
    uvicorn.run(
        "agenthive.lab.server:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def list_scenarios() -> None:
    """List all available attack scenario categories."""
    from agenthive.models import AttackCategory

    table = Table(title="Available Attack Scenarios")
    table.add_column("Category", style="cyan")
    table.add_column("Description", style="white")

    descriptions = {
        "tool_drift": "Exploit tool derivation caused by shared memory between agents",
        "long_horizon": "RL-based attacks spanning multiple agents in sequence",
        "collaboration_attack": "Manipulation of agent-to-agent collaboration",
        "authority_hijack": "Hijacking the authority chain between agents",
        "cross_agent_injection": "Prompt injection that propagates across agents",
        "multi_agent_ssrf": "Coordinated SSRF through multiple agents",
        "swarm_poisoning": "Poison one agent that propagates to the swarm",
        "identity_spoofing": "Identity spoofing between agents",
    }

    for cat in AttackCategory:
        table.add_row(cat.value, descriptions.get(cat.value, ""))

    console.print(table)


if __name__ == "__main__":
    app()
