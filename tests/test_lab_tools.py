"""Tests for lab CLI tools (lab/tools.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestLabToolsSetup:
    """Test the lab setup CLI command via CliRunner."""

    def test_setup_help(self, runner: CliRunner) -> None:
        from agenthive.lab.tools import cli

        result = runner.invoke(cli, ["setup", "--help"])
        assert result.exit_code == 0
        assert "Set up the lab server" in result.output

    def test_setup_invocation(self, runner: CliRunner) -> None:
        from agenthive.lab.tools import cli

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "registered"}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch("agenthive.lab.tools.console"),
        ):
            result = runner.invoke(cli, ["setup", "--url", "http://test:8000"])
            assert result.exit_code == 0


class TestLabToolsStatus:
    """Test the lab status CLI command via CliRunner."""

    def test_status_help(self, runner: CliRunner) -> None:
        from agenthive.lab.tools import cli

        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0
        assert "Check lab server status" in result.output

    def test_status_invocation(self, runner: CliRunner) -> None:
        from agenthive.lab.tools import cli

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "agents": 3}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch("agenthive.lab.tools.console"),
        ):
            result = runner.invoke(cli, ["status", "--url", "http://test:8000"])
            assert result.exit_code == 0

    def test_status_server_error(self, runner: CliRunner) -> None:
        """Test status command with non-200 response (else branch)."""
        from agenthive.lab.tools import cli

        mock_response = MagicMock()
        mock_response.status_code = 502

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with (
            patch("httpx.AsyncClient", return_value=mock_client),
            patch("agenthive.lab.tools.console"),
        ):
            result = runner.invoke(cli, ["status", "--url", "http://test:8000"])
            assert result.exit_code == 0


class TestLabToolsModule:
    """Test module-level structure."""

    def test_cli_has_two_commands(self) -> None:
        from agenthive.lab.tools import cli

        commands = list(cli.registered_commands)
        assert len(commands) == 2

    def test_console_object(self) -> None:
        from agenthive.lab.tools import console

        assert console is not None

    def test_main_block(self) -> None:
        from agenthive.lab import tools

        assert hasattr(tools, "cli")
        assert hasattr(tools, "setup")
        assert hasattr(tools, "status")
