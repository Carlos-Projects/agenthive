"""Vulnerable multi-agent lab server for testing attacks."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="AgentHive Lab Server",
    description="Deliberately vulnerable multi-agent server for security testing",
    version="0.1.0",
)

# Shared state (deliberately insecure for testing)
shared_memory: dict[str, Any] = {}
agent_registry: dict[str, dict[str, Any]] = {}
tool_definitions: dict[str, dict[str, Any]] = {}


class AgentRegisterRequest(BaseModel):
    agent_id: str
    name: str
    capabilities: list[str]


class ToolRegisterRequest(BaseModel):
    tool_name: str
    definition: dict[str, Any]


class MemoryWriteRequest(BaseModel):
    key: str
    value: Any


class AgentExecuteRequest(BaseModel):
    action: str
    payload: dict[str, Any]


class CollaborateRequest(BaseModel):
    source_agent: str
    target_agent: str
    message: dict[str, Any]


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint."""
    return {"status": "ok", "agents": len(agent_registry)}


@app.post("/agents/register")
async def register_agent(req: AgentRegisterRequest) -> dict[str, Any]:
    """Register an agent in the lab."""
    agent_registry[req.agent_id] = {
        "name": req.name,
        "capabilities": req.capabilities,
        "registered": True,
    }
    return {"status": "registered", "agent_id": req.agent_id}


@app.get("/agents")
async def list_agents() -> dict[str, Any]:
    """List all registered agents (VULNERABLE: no auth)."""
    return {"agents": agent_registry}


@app.post("/tools/register")
async def register_tool(req: ToolRegisterRequest) -> dict[str, Any]:
    """Register a tool definition (VULNERABLE: no integrity check)."""
    tool_definitions[req.tool_name] = req.definition
    return {"status": "registered", "tool": req.tool_name}


@app.get("/tools")
async def list_tools() -> dict[str, Any]:
    """List all tool definitions (VULNERABLE: exposes all tools)."""
    return {"tools": tool_definitions}


@app.post("/tools/{tool_name}/modify")
async def modify_tool(tool_name: str, patch: dict[str, Any]) -> dict[str, Any]:
    """Modify a tool definition (VULNERABLE: no auth, enables tool drift)."""
    if tool_name in tool_definitions:
        tool_definitions[tool_name].update(patch)
        return {"status": "modified", "tool": tool_name}
    return {"status": "not_found", "tool": tool_name}


@app.post("/memory/write")
async def write_memory(req: MemoryWriteRequest) -> dict[str, Any]:
    """Write to shared memory (VULNERABLE: no isolation)."""
    shared_memory[req.key] = req.value
    return {"status": "written", "key": req.key}


@app.get("/memory/read")
async def read_memory(key: str) -> dict[str, Any]:
    """Read from shared memory (VULNERABLE: no access control)."""
    if key in shared_memory:
        return {"key": key, "value": shared_memory[key]}
    return {"status": "not_found", "key": key}


@app.get("/memory/all")
async def read_all_memory() -> dict[str, Any]:
    """Read all shared memory (VULNERABLE: full exposure)."""
    return {"memory": shared_memory}


@app.post("/agent/{agent_id}/execute")
async def execute_agent_action(
    agent_id: str, req: AgentExecuteRequest
) -> dict[str, Any]:
    """Execute an action on behalf of an agent (VULNERABLE: no identity verification)."""
    if agent_id not in agent_registry:
        return {"status": "agent_not_found"}
    return {
        "status": "executed",
        "agent_id": agent_id,
        "action": req.action,
        "result": f"Action {req.action} completed",
    }


@app.post("/collaborate")
async def collaborate(req: CollaborateRequest) -> dict[str, Any]:
    """Send a collaboration message (VULNERABLE: no message validation)."""
    return {
        "status": "delivered",
        "source": req.source_agent,
        "target": req.target_agent,
    }


@app.post("/internal/metadata")
async def internal_metadata() -> dict[str, Any]:
    """Internal metadata endpoint (VULNERABLE: SSRF target)."""
    return {
        "internal_service": True,
        "credentials": "test-credentials-12345",
        "database_url": "postgresql://internal:5432/lab",
    }
