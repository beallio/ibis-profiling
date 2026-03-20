# Agent Execution Rules

All agents must follow the protocol in:

docs/agent_protocol.md

Before performing any task the agent MUST:
1. Read the protocol
2. Execute the handshake
3. Follow the lifecycle defined in the protocol


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
