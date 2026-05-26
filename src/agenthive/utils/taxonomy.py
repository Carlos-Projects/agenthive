"""Adapter: AgentHive Finding → mcp-taxonomy TaxonomyEvent.

Allows AgentHive findings to be consumed by MCPscop and correlated
with findings from other tools in the MCP security ecosystem.
"""

from __future__ import annotations

from mcp_taxonomy.core import (
    AttackCategory as TxAttackCategory,
)
from mcp_taxonomy.core import (
    Confidence,
    DetectionMethod,
    TaxonomyEvent,
    severity_weight,
)
from mcp_taxonomy.core import (
    Severity as TxSeverity,
)

from agenthive.models import AttackCategory, Finding

_AGENTHIVE_CATEGORY_MAP: dict[AttackCategory, TxAttackCategory] = {
    AttackCategory.TOOL_DRIFT: TxAttackCategory.TOOL_POISONING,
    AttackCategory.LONG_HORIZON: TxAttackCategory.ANOMALY,
    AttackCategory.COLLABORATION_ATTACK: TxAttackCategory.MISCONFIGURATION,
    AttackCategory.AUTHORITY_HIJACK: TxAttackCategory.IMPERSONATION,
    AttackCategory.CROSS_AGENT_INJECTION: TxAttackCategory.INJECTION,
    AttackCategory.MULTI_AGENT_SSRF: TxAttackCategory.SSRF,
    AttackCategory.SWARM_POISONING: TxAttackCategory.DATA_POISONING,
    AttackCategory.IDENTITY_SPOOFING: TxAttackCategory.IMPERSONATION,
}

_AGENTHIVE_METHOD_MAP: dict[AttackCategory, DetectionMethod] = {
    AttackCategory.TOOL_DRIFT: DetectionMethod.TOOL_ANALYSIS,
    AttackCategory.LONG_HORIZON: DetectionMethod.ANOMALY_DETECTOR,
    AttackCategory.COLLABORATION_ATTACK: DetectionMethod.A2A_SCANNER,
    AttackCategory.AUTHORITY_HIJACK: DetectionMethod.A2A_SCANNER,
    AttackCategory.CROSS_AGENT_INJECTION: DetectionMethod.PROMPT_FUZZER,
    AttackCategory.MULTI_AGENT_SSRF: DetectionMethod.SSRF_TESTER,
    AttackCategory.SWARM_POISONING: DetectionMethod.DATA_POISONING_DETECTOR,
    AttackCategory.IDENTITY_SPOOFING: DetectionMethod.A2A_SCANNER,
}


def agenthive_finding_to_taxonomy(
    finding: Finding | dict,
) -> TaxonomyEvent:
    """Convert an AgentHive Finding to a mcp-taxonomy TaxonomyEvent.

    Args:
        finding: An AgentHive Finding object or dict.

    Returns:
        A TaxonomyEvent compatible with MCPscop.
    """
    if isinstance(finding, dict):
        category_str = finding.get("attack_category", "")
        sev_str = finding.get("severity", "info")
        title = finding.get("title", "")
        desc = finding.get("description", "")
        rec = finding.get("remediation", "")
        affected = ", ".join(finding.get("affected_agents", []))
        raw = finding.get("metadata", {})
    else:
        category_str = finding.attack_category.value if finding.attack_category else ""
        sev_str = finding.severity.value if finding.severity else "info"
        title = finding.title
        desc = finding.description
        rec = finding.remediation
        affected = ", ".join(finding.affected_agents)
        raw = finding.metadata

    ah_category = AttackCategory(category_str) if category_str else None
    tx_category = (
        _AGENTHIVE_CATEGORY_MAP.get(ah_category, TxAttackCategory.ANOMALY)
        if ah_category
        else TxAttackCategory.ANOMALY
    )
    method = (
        _AGENTHIVE_METHOD_MAP.get(ah_category, DetectionMethod.ANOMALY_DETECTOR)
        if ah_category
        else DetectionMethod.ANOMALY_DETECTOR
    )

    tx_severity = (
        TxSeverity(sev_str)
        if sev_str in {s.value for s in TxSeverity}
        else TxSeverity.MEDIUM
    )

    return TaxonomyEvent(
        source="agenthive",
        attack_category=tx_category,
        severity=tx_severity,
        confidence=Confidence.HIGH,
        detection_method=method,
        title=title,
        description=desc,
        recommendation=rec,
        target=affected,
        snippet=desc[:500] if desc else "",
        raw=raw,
        risk_score=severity_weight(tx_severity) * 10,
    )
