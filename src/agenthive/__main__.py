from agenthive.cli import app

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        from rich.console import Console

        console = Console()
        console.print(f"\n[red]Error:[/red] {e}")
        raise SystemExit(1) from e
