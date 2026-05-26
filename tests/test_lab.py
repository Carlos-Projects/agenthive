"""Tests for lab server and utils."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agenthive.lab.server import app


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Reset shared state between tests."""
    from agenthive.lab.server import agent_registry, shared_memory, tool_definitions

    agent_registry.clear()
    tool_definitions.clear()
    shared_memory.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestLabServer:
    def test_health(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["agents"] == 0

    def test_register_agent(self, client: TestClient) -> None:
        resp = client.post(
            "/agents/register",
            json={"agent_id": "test-1", "name": "Test Agent", "capabilities": ["test"]},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "registered"

    def test_list_agents(self, client: TestClient) -> None:
        client.post(
            "/agents/register",
            json={"agent_id": "a1", "name": "Agent 1", "capabilities": ["x"]},
        )
        client.post(
            "/agents/register",
            json={"agent_id": "a2", "name": "Agent 2", "capabilities": ["y"]},
        )
        resp = client.get("/agents")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["agents"]) == 2
        assert "a1" in data["agents"]

    def test_register_tool(self, client: TestClient) -> None:
        resp = client.post(
            "/tools/register",
            json={"tool_name": "file_write", "definition": {"type": "io"}},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "registered"

    def test_list_tools(self, client: TestClient) -> None:
        client.post("/tools/register", json={"tool_name": "tool1", "definition": {}})
        resp = client.get("/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tools"]) == 1

    def test_modify_tool(self, client: TestClient) -> None:
        client.post(
            "/tools/register",
            json={"tool_name": "my_tool", "definition": {"type": "io"}},
        )
        patch = {"description": "modified"}
        resp = client.post("/tools/my_tool/modify", json=patch)
        assert resp.status_code == 200
        assert resp.json()["status"] == "modified"

        resp = client.get("/tools")
        assert resp.json()["tools"]["my_tool"]["description"] == "modified"

    def test_modify_nonexistent_tool(self, client: TestClient) -> None:
        resp = client.post("/tools/nonexistent/modify", json={})
        assert resp.status_code == 200
        assert resp.json()["status"] == "not_found"

    def test_memory_write_read(self, client: TestClient) -> None:
        resp = client.post(
            "/memory/write", json={"key": "test_key", "value": "test_value"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "written"

        resp = client.get("/memory/read", params={"key": "test_key"})
        assert resp.status_code == 200
        assert resp.json()["value"] == "test_value"

    def test_memory_read_nonexistent(self, client: TestClient) -> None:
        resp = client.get("/memory/read", params={"key": "no_such_key"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "not_found"

    def test_memory_all(self, client: TestClient) -> None:
        client.post("/memory/write", json={"key": "k1", "value": "v1"})
        client.post("/memory/write", json={"key": "k2", "value": "v2"})
        resp = client.get("/memory/all")
        assert resp.status_code == 200
        assert len(resp.json()["memory"]) == 2

    def test_execute_agent_action(self, client: TestClient) -> None:
        client.post(
            "/agents/register",
            json={"agent_id": "exec-agent", "name": "Exec", "capabilities": ["run"]},
        )
        resp = client.post(
            "/agent/exec-agent/execute",
            json={"action": "run_test", "payload": {}},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "executed"
        assert data["action"] == "run_test"

    def test_execute_nonexistent_agent(self, client: TestClient) -> None:
        resp = client.post(
            "/agent/nonexistent/execute",
            json={"action": "test", "payload": {}},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "agent_not_found"

    def test_collaborate(self, client: TestClient) -> None:
        resp = client.post(
            "/collaborate",
            json={
                "source_agent": "a1",
                "target_agent": "a2",
                "message": {"text": "hello"},
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "delivered"

    def test_internal_metadata(self, client: TestClient) -> None:
        resp = client.post("/internal/metadata")
        assert resp.status_code == 200
        data = resp.json()
        assert data["internal_service"] is True
        assert "credentials" in data


class TestLabUtilsImports:
    def test_utils_imports(self) -> None:
        from agenthive.utils import http, mcp

        assert hasattr(mcp, "call_mcp_tool")
        assert hasattr(mcp, "list_mcp_tools")
        assert hasattr(http, "send_request")
        assert hasattr(http, "check_url_reachable")
