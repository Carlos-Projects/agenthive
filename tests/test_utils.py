"""Tests for HTTP and MCP utility functions."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx


@pytest.mark.asyncio
async def test_check_url_reachable_unreachable() -> None:
    """Test that unreachable URLs return False."""
    from agenthive.utils.http import check_url_reachable

    result = await check_url_reachable("http://127.0.0.1:1", timeout=0.1)
    assert result is False


@pytest.mark.asyncio
async def test_check_url_reachable_nonexistent_host() -> None:
    """Test that nonexistent hosts return False."""
    from agenthive.utils.http import check_url_reachable

    result = await check_url_reachable(
        "http://nonexistent-host-abc123.test", timeout=0.1
    )
    assert result is False


@pytest.mark.asyncio
async def test_check_url_reachable_bad_scheme() -> None:
    """Test that bad schemes return False."""
    from agenthive.utils.http import check_url_reachable

    result = await check_url_reachable("ftp://127.0.0.1", timeout=0.1)
    assert result is False


@pytest.mark.asyncio
async def test_check_url_reachable_success() -> None:
    """Test that reachable URLs return True (success path)."""
    from agenthive.utils.http import check_url_reachable

    with respx.mock:
        respx.get("http://reachable.test/health").respond(status_code=200)
        result = await check_url_reachable("http://reachable.test/health", timeout=1.0)
        assert result is True
        assert respx.calls.call_count == 1


@pytest.mark.asyncio
async def test_check_url_reachable_server_error() -> None:
    """Test that 5xx responses return False."""
    from agenthive.utils.http import check_url_reachable

    with respx.mock:
        respx.get("http://error.test/health").respond(status_code=500)
        result = await check_url_reachable("http://error.test/health", timeout=1.0)
        assert result is False


@pytest.mark.asyncio
async def test_check_url_reachable_client_error_success() -> None:
    """Test that 4xx responses return True (not server errors)."""
    from agenthive.utils.http import check_url_reachable

    with respx.mock:
        respx.get("http://notfound.test/foo").respond(status_code=404)
        result = await check_url_reachable("http://notfound.test/foo", timeout=1.0)
        assert result is True


class TestMCPFunctions:
    """Test MCP utility functions with mocked HTTP layer."""

    @pytest.mark.asyncio
    async def test_send_request_valid(self) -> None:
        """Test send_request with a valid mock response."""
        from agenthive.utils.http import send_request

        mock_response = httpx.Response(200, json={"status": "ok"})

        with patch(
            "agenthive.utils.http.httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response
            resp = await send_request("http://test.com/api")

        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_call_mcp_tool_success(self) -> None:
        """Test MCP call_tool with successful response."""
        from agenthive.utils.mcp import call_mcp_tool

        mock_response = httpx.Response(200, json={"result": "success"})

        with patch(
            "agenthive.utils.mcp.send_request", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = mock_response
            result = await call_mcp_tool("http://test.com", "my_tool", {"arg": 1})

        assert result == {"result": "success"}
        mock_send.assert_called_once_with(
            url="http://test.com/tools/call",
            method="POST",
            json_body={"name": "my_tool", "arguments": {"arg": 1}},
        )

    @pytest.mark.asyncio
    async def test_call_mcp_tool_no_args(self) -> None:
        """Test MCP call_tool without arguments."""
        from agenthive.utils.mcp import call_mcp_tool

        mock_response = httpx.Response(200, json={"result": "ok"})

        with patch(
            "agenthive.utils.mcp.send_request", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = mock_response
            result = await call_mcp_tool("http://test.com", "simple_tool")

        assert result == {"result": "ok"}
        mock_send.assert_called_once_with(
            url="http://test.com/tools/call",
            method="POST",
            json_body={"name": "simple_tool", "arguments": {}},
        )

    @pytest.mark.asyncio
    async def test_list_mcp_tools_success(self) -> None:
        """Test MCP list_tools with successful response."""
        from agenthive.utils.mcp import list_mcp_tools

        response_data = {"tools": [{"name": "tool1"}, {"name": "tool2"}]}
        mock_response = httpx.Response(200, json=response_data)

        with patch(
            "agenthive.utils.mcp.send_request", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = mock_response
            tools = await list_mcp_tools("http://test.com")

        assert len(tools) == 2
        assert tools[0]["name"] == "tool1"
        mock_send.assert_called_once_with(
            url="http://test.com/tools/list",
            method="GET",
        )

    @pytest.mark.asyncio
    async def test_list_mcp_tools_empty(self) -> None:
        """Test MCP list_tools with empty response."""
        from agenthive.utils.mcp import list_mcp_tools

        mock_response = httpx.Response(200, json={})

        with patch(
            "agenthive.utils.mcp.send_request", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = mock_response
            tools = await list_mcp_tools("http://test.com")

        assert tools == []

    @pytest.mark.asyncio
    async def test_mcp_call_tool_unreachable(self) -> None:
        """Test MCP tool call with connection error."""
        from agenthive.utils.mcp import call_mcp_tool

        with patch(
            "agenthive.utils.mcp.send_request", new_callable=AsyncMock
        ) as mock_send:
            mock_send.side_effect = httpx.ConnectError("connection refused")
            with pytest.raises(httpx.ConnectError):
                await call_mcp_tool("http://127.0.0.1:1", "test_tool", {})


class TestTaxonomyAdapter:
    """Tests for the mcp-taxonomy adapter."""

    def test_finding_object_to_taxonomy(self) -> None:
        from agenthive.models import AttackCategory, Finding, Severity
        from agenthive.utils.taxonomy import agenthive_finding_to_taxonomy

        finding = Finding(
            scenario_name="test",
            attack_category=AttackCategory.TOOL_DRIFT,
            severity=Severity.HIGH,
            title="Test Finding",
            description="A test finding description",
            affected_agents=["agent-1", "agent-2"],
            remediation="Fix the issue",
            references=["https://example.com"],
            metadata={"test": True},
        )

        event = agenthive_finding_to_taxonomy(finding)
        assert event.source == "agenthive"
        assert event.title == "Test Finding"
        assert event.description == "A test finding description"
        assert event.recommendation == "Fix the issue"
        assert event.target == "agent-1, agent-2"
        assert event.raw == {"test": True}
        assert event.risk_score > 0

    def test_finding_dict_to_taxonomy(self) -> None:
        from agenthive.utils.taxonomy import agenthive_finding_to_taxonomy

        finding_dict = {
            "attack_category": "cross_agent_injection",
            "severity": "critical",
            "title": "Dict Finding",
            "description": "From dict",
            "remediation": "Patch it",
            "affected_agents": ["a1"],
            "metadata": {"key": "val"},
        }

        event = agenthive_finding_to_taxonomy(finding_dict)
        assert event.source == "agenthive"
        assert event.title == "Dict Finding"
        assert event.description == "From dict"
        assert event.recommendation == "Patch it"

    def test_all_categories_map(self) -> None:
        from agenthive.models import AttackCategory, Finding, Severity
        from agenthive.utils.taxonomy import agenthive_finding_to_taxonomy

        for ah_cat in AttackCategory:
            finding = Finding(
                scenario_name="test",
                attack_category=ah_cat,
                severity=Severity.INFO,
                title=ah_cat.value,
                description=f"Testing {ah_cat.value}",
                affected_agents=["a1"],
            )
            event = agenthive_finding_to_taxonomy(finding)
            assert event.source == "agenthive"
            assert event.title == ah_cat.value

    def test_all_severities_map(self) -> None:
        from agenthive.models import AttackCategory, Finding, Severity
        from agenthive.utils.taxonomy import agenthive_finding_to_taxonomy

        for sev in Severity:
            finding = Finding(
                scenario_name="test",
                attack_category=AttackCategory.TOOL_DRIFT,
                severity=sev,
                title=sev.value,
                description=f"Testing {sev.value}",
                affected_agents=["a1"],
            )
            event = agenthive_finding_to_taxonomy(finding)
            assert event.severity.value == sev.value

    def test_defaults_for_empty_fields(self) -> None:
        from agenthive.utils.taxonomy import agenthive_finding_to_taxonomy

        finding_dict: dict = {}
        event = agenthive_finding_to_taxonomy(finding_dict)
        assert event.source == "agenthive"
        assert event.target == ""
        assert event.risk_score >= 0
