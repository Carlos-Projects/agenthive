# AgentHive

Multi-agent attack simulation framework for AI systems.

[![PyPI](https://img.shields.io/pypi/v/agenthive-sim.svg)](https://pypi.org/project/agenthive-sim/)
[![Python](https://img.shields.io/pypi/pyversions/agenthive-sim.svg)](https://pypi.org/project/agenthive-sim/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/Carlos-Projects/agenthive/actions/workflows/ci.yml/badge.svg)](https://github.com/Carlos-Projects/agenthive/actions/workflows/ci.yml)

AgentHive extends [mcpwn](https://github.com/Carlos-Projects/mcpwn) from the single-agent domain to the **multi-agent domain**, modeling attacks that are only possible when multiple AI agents interact with each other.

## Installation

```bash
pip install agenthive-sim
```

For development:

```bash
pip install -e ".[dev,lab]"
```

## Quick Start

```bash
# Generate a scenario template
agenthive scenario my-scenario -o scenario.yaml

# Run a simulation
agenthive simulate scenario.yaml -v

# List available attack categories
agenthive list-scenarios

# Start the vulnerable lab server
agenthive lab
```

## Attack Scenarios

| Category | Description | Severity |
|---|---|---|
| `tool_drift` | Exploit tool derivation caused by shared memory between agents | High |
| `long_horizon` | RL-based attacks spanning multiple agents in sequence | Critical |
| `collaboration_attack` | Manipulation of agent-to-agent collaboration | High |
| `authority_hijack` | Hijacking the authority chain between agents | Critical |
| `cross_agent_injection` | Prompt injection that propagates across agents | Critical |
| `multi_agent_ssrf` | Coordinated SSRF through multiple agents | High |
| `swarm_poisoning` | Poison one agent that propagates to the swarm | Critical |
| `identity_spoofing` | Identity spoofing between agents | High |

## Academic References

- [Evo-Attacker: Memory-Augmented RL for Long-Horizon Tool Attacks](https://arxiv.org/abs/2605.25389) (ACL 2026)
- [Memory-Induced Tool-Drift in LLM Agents](https://arxiv.org/abs/2605.24941)
- [Behind EvoMap: Agent-to-Agent Collaboration Network](https://arxiv.org/abs/2605.25815)
- [Authority Frontier Framework for Runtime Actuarial Control](https://arxiv.org/abs/2605.25632)
- [Deep-Research Agents Can Be Poisoned](https://arxiv.org/abs/2605.24294) (Shmatikov et al.)
- [MITRE ATLAS — Multi-Agent System Attack Patterns](https://atlas.mitre.org/techniques/)

## Ecosystem

- Extends [mcpwn](https://github.com/Carlos-Projects/mcpwn) — same stack, multi-agent domain
- Uses [mcp-taxonomy](https://github.com/Carlos-Projects/mcp-taxonomy)
- Reports consumable by [MCPscop](https://github.com/Carlos-Projects/mcpscope)

## License

MIT — see [LICENSE](LICENSE)
