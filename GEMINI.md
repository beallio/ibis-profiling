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

Requirements:

• Planning documents in docs/plans/
• Tests must exist before implementation
• All caches redirected to /tmp/{project}
• Virtual environment must exist in /tmp/{project}/.venv
