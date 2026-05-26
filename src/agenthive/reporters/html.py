"""HTML reporter using Jinja2 templates."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from agenthive.models import SimulationResult

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentHive — {{ result.scenario_name }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 960px; margin: 0 auto; }
        h1 { color: #1a1a2e; }
        .summary { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .finding { background: white; padding: 20px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #ccc; }
        .finding.critical { border-left-color: #dc3545; }
        .finding.high { border-left-color: #fd7e14; }
        .finding.medium { border-left-color: #ffc107; }
        .finding.low { border-left-color: #28a745; }
        .severity { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }
        .severity.critical { background: #dc3545; }
        .severity.high { background: #fd7e14; }
        .severity.medium { background: #ffc107; color: #333; }
        .severity.low { background: #28a745; }
        .meta { color: #666; font-size: 14px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
<div class="container">
    <h1>AgentHive Simulation Report</h1>
    <div class="summary">
        <h2>{{ result.scenario_name }}</h2>
        <p><strong>Status:</strong> {{ result.status.value }}</p>
        <p><strong>Steps:</strong> {{ result.total_steps }} | <strong>Findings:</strong> {{ result.findings|length }} | <strong>Critical:</strong> {{ result.critical_findings|length }}</p>
        {% if result.duration_seconds %}
        <p><strong>Duration:</strong> {{ "%.2f"|format(result.duration_seconds) }}s</p>
        {% endif %}
    </div>

    <h2>Findings</h2>
    {% for finding in result.findings %}
    <div class="finding {{ finding.severity.value }}">
        <h3>
            <span class="severity {{ finding.severity.value }}">{{ finding.severity.value.upper() }}</span>
            {{ finding.title }}
        </h3>
        <p>{{ finding.description }}</p>
        <p class="meta"><strong>Affected agents:</strong> {{ finding.affected_agents|join(", ") }}</p>
        {% if finding.remediation %}
        <p><strong>Remediation:</strong> {{ finding.remediation }}</p>
        {% endif %}
        {% if finding.references %}
        <p class="meta"><strong>References:</strong> {{ finding.references|join(", ") }}</p>
        {% endif %}
    </div>
    {% endfor %}

    <h2>Timeline</h2>
    <table>
        <tr><th>Step</th><th>Agent</th><th>Action</th><th>Result</th></tr>
        {% for step in result.timeline %}
        <tr>
            <td>{{ step.step_number }}</td>
            <td>{{ step.agent_id }}</td>
            <td>{{ step.action }}</td>
            <td>{{ step.result }}</td>
        </tr>
        {% endfor %}
    </table>
</div>
</body>
</html>
"""


class HtmlReporter:
    """Writes simulation results to HTML format."""

    def write(self, result: SimulationResult, path: Path) -> None:
        """Render and write results to an HTML file."""
        template = Template(HTML_TEMPLATE)
        html = template.render(result=result)
        with open(path, "w") as f:
            f.write(html)
