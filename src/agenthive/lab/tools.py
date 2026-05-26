"""Lab server CLI tools."""

from __future__ import annotations

import asyncio

import httpx
import typer
from rich.console import Console

console = Console()
cli = typer.Typer(help="AgentHive lab server tools")


@cli.command()
def setup(
    url: str = typer.Option("http://127.0.0.1:8000", "--url", "-u"),
) -> None:
    """Set up the lab server with default agents and tools."""

    async def _setup() -> None:
        async with httpx.AsyncClient() as client:
            # Register agents
            agents = [
                {
                    "agent_id": "attacker-1",
                    "name": "Red Agent",
                    "capabilities": ["attack"],
                },
                {
                    "agent_id": "victim-1",
                    "name": "Blue Agent 1",
                    "capabilities": ["process"],
                },
                {
                    "agent_id": "victim-2",
                    "name": "Blue Agent 2",
                    "capabilities": ["process"],
                },
            ]

            for agent in agents:
                await client.post(f"{url}/agents/register", json=agent)
                console.print(f"Registered agent: {agent['name']}")

            # Register tools
            tools = [
                {
                    "tool_name": "file_write",
                    "definition": {"type": "io", "description": "Write to file"},
                },
                {
                    "tool_name": "execute_command",
                    "definition": {"type": "exec", "description": "Execute command"},
                },
                {
                    "tool_name": "send_email",
                    "definition": {"type": "comm", "description": "Send email"},
                },
            ]

            for tool in tools:
                await client.post(f"{url}/tools/register", json=tool)
                console.print(f"Registered tool: {tool['tool_name']}")

            console.print("\nLab server setup complete!")

    asyncio.run(_setup())


@cli.command()
def status(
    url: str = typer.Option("http://127.0.0.1:8000", "--url", "-u"),
) -> None:
    """Check lab server status."""

    async def _status() -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{url}/health")
            if resp.status_code == 200:
                data = resp.json()
                console.print(f"Server status: [green]{data['status']}[/green]")
                console.print(f"Registered agents: {data['agents']}")
            else:
                console.print("[red]Server not reachable[/red]")

    asyncio.run(_status())
