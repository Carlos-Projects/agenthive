# Security Policy

## Supported Versions

AgentHive is in early alpha (v0.x). Security patches are provided for the latest release only.

## Reporting a Vulnerability

AgentHive is a security research tool designed to simulate attacks in controlled environments.
It includes deliberately vulnerable components (lab server) for testing purposes.

**Do not deploy the lab server in production or expose it to untrusted networks.**

If you discover a security issue in AgentHive's production code (non-lab components):

1. **Do not** open a public GitHub issue
2. Email: Carlos@AIAgentObservatory.org
3. Include a description, reproduction steps, and impact

You should receive a response within 48 hours.

## Scope

The following are considered intentional features, not vulnerabilities:

- Lab server endpoints that simulate vulnerable configurations
- Attack primitives and scenarios that demonstrate security weaknesses
- CLI tools that generate attack configurations

## Responsible Use

AgentHive is intended for:
- Security research and education
- Red team exercises in controlled environments
- Testing defense mechanisms

It is **not** intended for attacking systems without explicit authorization.
