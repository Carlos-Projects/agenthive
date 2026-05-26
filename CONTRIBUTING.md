# Contributing to AgentHive

We welcome contributions! This doc explains how to set up, develop, and submit changes.

## Setup

```bash
# Clone and install
git clone https://github.com/Carlos-Projects/agenthive.git
cd agenthive
pip install -e ".[dev,lab]"
```

## Development

```bash
# Lint
ruff check src/ tests/

# Type check
mypy src/agenthive

# Test
python -m pytest tests/ -v

# Coverage
python -m pytest tests/ --cov=agenthive --cov-report=html
```

## Project Structure

```
src/agenthive/
├── cli.py           # Typer CLI entry points
├── models.py        # Pydantic data models
├── simulator.py     # Core simulation engine
├── scenarios/       # Attack scenario implementations (one per category)
├── agents/          # Agent role implementations
├── attacks/         # Attack primitive modules
├── lab/             # Lab server (FastAPI) + CLI tools
├── reporters/       # Output formatters (console, json, html, sarif)
└── utils/           # Shared utilities (http, mcp)
```

## Adding a New Attack Scenario

1. Create `src/agenthive/scenarios/<name>.py` with an async handler function
2. Add the category to `AttackCategory` in `models.py`
3. Register the handler in `scenarios/__init__.py`
4. Add tests in `tests/test_scenarios/`
5. Add the scenario template to `get_scenario_template()` in `scenarios/__init__.py`

## Code Conventions

- Python 3.11+ type hints throughout
- 88 char line length (ruff default)
- Async for all I/O operations
- Pydantic models for all data structures
- Test coverage > 80% for new code

## PR Checklist

- [ ] `ruff check src/ tests/` passes
- [ ] `mypy src/agenthive` passes
- [ ] All tests pass (`python -m pytest tests/ -v`)
- [ ] Coverage does not decrease
- [ ] New scenarios have corresponding tests
