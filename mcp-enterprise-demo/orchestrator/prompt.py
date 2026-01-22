def build_agent_prompt(user_prompt: str, user: dict, trace_id: str) -> str:
    """
    Compose the instruction given to the LangChain agent.
    The agent SHOULD use the provided tools only and MUST NOT bypass MCP authorization.
    We explicitly instruct the agent to call tools with JSON payloads.
    """
    return f"""
You are the orchestrator agent. You have these trusted tools available (authorize, evaluate_risk, approve, execute_action, query_observability, check_secret_path, log_audit).
Do NOT access any services directly or bypass authorization.

User: {user}
TraceId: {trace_id}

Task: {user_prompt}

Strict rules:
- For any action, first call "authorize" tool with JSON: {{'user': <user dict>, 'action': '<action>', 'trace_id': '{trace_id}'}}.
- If action is high-risk (restart_service), call "evaluate_risk" and if requires approval call "approve".
- To execute, call "execute_action" only after authorization and approval.
- Always call "log_audit" with a final audit entry containing user_id, action, result, reason, trace_id.

Return a JSON string describing the flow and the final outcome.
"""
DEFAULT_PROMPT = """
User requests an action. If it contains 'restart' treat as restart_service. Otherwise handle as a query.
"""
