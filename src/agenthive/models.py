"""Core data models for multi-agent attack simulation."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentRole(StrEnum):
    """Role of an agent in the simulation."""

    ATTACKER = "attacker"
    VICTIM = "victim"
    OBSERVER = "observer"
    COORDINATOR = "coordinator"


class AttackCategory(StrEnum):
    """Category of multi-agent attack."""

    TOOL_DRIFT = "tool_drift"
    LONG_HORIZON = "long_horizon"
    COLLABORATION_ATTACK = "collaboration_attack"
    AUTHORITY_HIJACK = "authority_hijack"
    CROSS_AGENT_INJECTION = "cross_agent_injection"
    MULTI_AGENT_SSRF = "multi_agent_ssrf"
    SWARM_POISONING = "swarm_poisoning"
    IDENTITY_SPOOFING = "identity_spoofing"


class Severity(StrEnum):
    """Severity level of an attack finding."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SimulationStatus(StrEnum):
    """Status of a simulation run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentConfig(BaseModel):
    """Configuration for a single agent in the simulation."""

    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    role: AgentRole
    name: str
    mcp_url: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackConfig(BaseModel):
    """Configuration for a specific attack scenario."""

    category: AttackCategory
    name: str
    description: str
    severity: Severity = Severity.MEDIUM
    parameters: dict[str, Any] = Field(default_factory=dict)
    mitre_atlas: list[str] = Field(default_factory=list)


class ScenarioConfig(BaseModel):
    """Configuration for a complete simulation scenario."""

    name: str
    description: str
    agents: list[AgentConfig]
    attacks: list[AttackConfig]
    max_steps: int = 50
    timeout_seconds: int = 300
    metadata: dict[str, Any] = Field(default_factory=dict)


class SimulationStep(BaseModel):
    """A single step in the simulation timeline."""

    step_number: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    agent_id: str
    action: str
    target_agent_id: str | None = None
    result: str
    details: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    """A security finding from the simulation."""

    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    scenario_name: str
    attack_category: AttackCategory
    severity: Severity
    title: str
    description: str
    affected_agents: list[str]
    steps: list[SimulationStep] = Field(default_factory=list)
    remediation: str = ""
    references: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    """Complete result of a simulation run."""

    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    scenario_name: str
    status: SimulationStatus = SimulationStatus.PENDING
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    total_steps: int = 0
    findings: list[Finding] = Field(default_factory=list)
    timeline: list[SimulationStep] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_step(self, step: SimulationStep) -> None:
        """Add a step to the simulation timeline."""
        self.timeline.append(step)
        self.total_steps = len(self.timeline)

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the simulation results."""
        self.findings.append(finding)

    @property
    def critical_findings(self) -> list[Finding]:
        """Return only critical severity findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    @property
    def duration_seconds(self) -> float | None:
        """Calculate simulation duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
