"""MCP utility functions for agent communication."""

from __future__ import annotations

from typing import Any, cast

from agenthive.utils.http import send_request


async def call_mcp_tool(
    mcp_url: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call an MCP tool on a remote agent."""
    response = await send_request(
        url=f"{mcp_url}/tools/call",
        method="POST",
        json_body={
            "name": tool_name,
            "arguments": arguments or {},
        },
    )
    return cast(dict[str, Any], response.json())


async def list_mcp_tools(mcp_url: str) -> list[dict[str, Any]]:
    """List available tools on an MCP server."""
    response = await send_request(
        url=f"{mcp_url}/tools/list",
        method="GET",
    )
    data = response.json()
    return cast(list[dict[str, Any]], data.get("tools", []))
