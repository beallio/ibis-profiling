# Agent Execution Protocol

Mandatory lifecycle:

ANALYZE
PLAN
TEST (RED)
IMPLEMENT (GREEN)
REFACTOR
VALIDATE
COMMIT
DOCUMENT

### Quality Control

Before any commit, agents MUST execute:

```bash
ruff check . --fix
ruff format .
uv run ty check src/
uv run pytest
```
