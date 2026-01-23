"""Agent builder and multi-step orchestration logic.

This module exposes a run_multi_step() helper that:
- clears the per-run action log
- instantiates a LangChain agent wired to safe tools
- instructs the agent to decompose the user's prompt into subtasks
- after the agent executes tools, collects action logs and produces a
  single natural-language summary describing what happened for the user.

This keeps all MCP governance intact because the tools themselves call
the Identity/Risk/Operations/Audit MCPs and enforce authorization.
"""

import os
import json
import uuid
from typing import Dict, Any, List, Optional

from orchestrator import tools as oc_tools
from orchestrator import prompt as oc_prompt


try:
    from langchain_classic.agents import initialize_agent, AgentType  # type: ignore
    LANGCHAIN_AVAILABLE = True
except Exception:
    LANGCHAIN_AVAILABLE = False

# Ollama-based lightweight classifier (fallback if LangChain is disabled)
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


def classify_intent_with_ai(prompt: str) -> str:
    system_prompt = (
        "You are an AI orchestrator. Classify into restart_service, query, forbidden, or unknown."
    )
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=10)
        r.raise_for_status()
        content = r.json().get("message", {}).get("content")
        if not content:
            return "unknown"
        parsed = json.loads(content)
        return parsed.get("action", "unknown")
    except Exception:
        return "unknown"

def _build_agent():
    """Build a LangChain agent wired to our tools.
    
    Prefers Ollama (local) if available, falls back to OpenRouter if OPENROUTER_API_KEY is set.
    """
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain not installed in the container")
    try:
        # Try Ollama first (no API key required)
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        
        try:
            from langchain_community.chat_models import ChatOllama  # type: ignore
            # Test if Ollama is reachable
            test_resp = requests.get(f"{ollama_url}/api/tags", timeout=2)
            if test_resp.status_code == 200:
                llm = ChatOllama(model=ollama_model, base_url=ollama_url, temperature=0)
                tools = oc_tools.get_langchain_tools()
                agent = initialize_agent(
                    tools, 
                    llm, 
                    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=10,
                    early_stopping_method="generate"
                )
                return agent
        except Exception as ollama_err:
            print(f"Ollama not available ({ollama_err}), trying OpenRouter...")
        
        # Fallback to OpenRouter (OpenAI-compatible API)
        from langchain_openai import ChatOpenAI  # type: ignore
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise RuntimeError("Neither Ollama nor OpenRouter is available. Set OPENROUTER_API_KEY or run Ollama at OLLAMA_URL.")
        
        # Use a free/low-cost model from OpenRouter
        # Check https://openrouter.ai/models for current free models
        model_name = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-nano-30b-a3b:free")
        llm = ChatOpenAI(
            temperature=0,
            model=model_name,
            openai_api_key=openrouter_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:8000",  # Optional: for rankings
                "X-Title": "MCP Enterprise Demo"  # Optional: for rankings
            }
        )
        tools = oc_tools.get_langchain_tools()
        agent = initialize_agent(
            tools, 
            llm, 
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="generate"
        )
        return agent
    except Exception as e:
        print(f"Failed to build LangChain agent: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError("Failed to build LangChain agent") from e


def _summarize_action_logs(logs: List[Dict[str, Any]], user: Dict[str, Any], agent_message: Optional[str] = None) -> str:
    """Create a single natural-language summary from action logs.

    This is deterministic and does not call any external LLMs, so the
    summary remains auditable and consistent with MCP results.
    """
    outcomes: List[str] = []

    # Pre-scan flags
    has_execute = any((entry.get("tool") == "execute_action") for entry in logs)
    has_approve_approved = any((entry.get("tool") == "approve" and isinstance(entry.get("result"), dict) and entry.get("result").get("approved")) for entry in logs)
    eval_requires_approval = any((entry.get("tool") == "evaluate_risk" and isinstance(entry.get("result"), dict) and entry.get("result").get("requires_approval")) for entry in logs)

    for entry in logs:
        tool = entry.get("tool")

        if tool == "execute_action":
            action = entry.get("action")
            result = entry.get("result")
            # If result is a dict with error -> denied
            if isinstance(result, dict) and result.get("error"):
                reason = result.get("reason") or result.get("error")
                outcomes.append(f"You are not authorized to {action.replace('_', ' ')} ({reason}).")
            else:
                # assume success
                outcomes.append(f"The {action.replace('_', ' ')} has been performed.")

        elif tool == "approve":
            # Only mention approval when it explicitly denied
            res = entry.get("result")
            if isinstance(res, dict) and res.get("approved") is False:
                outcomes.append("Approval was denied.")
            # otherwise skip mentioning approve

        elif tool == "query_observability":
            # For queries, present a brief confirmation (don't dump raw JSON)
            outcomes.append("Observability query returned results.")

        elif tool in ("authorize", "evaluate_risk", "log_audit", "check_secret"):
            # governance tools: handled implicitly; only surface if they block
            # we'll detect blocking via execute_action or approve entries
            pass

        else:
            # generic fallback for unexpected tools (rare)
            res = entry.get("result")
            outcomes.append(f"Tool {tool} returned: {res}")

    # Post-check: if risk required approval but no approval and no execution -> surface it
    if eval_requires_approval and not has_approve_approved and not has_execute:
        outcomes.append("The action required approval but was not approved.")

    # Build a friendly single response
    parts: List[str] = []
    if agent_message:
        parts.append(agent_message.strip())
    if outcomes:
        parts.append(" ".join(outcomes))
    if not parts:
        return "I processed your request but there was nothing actionable."
    return " ".join(parts)


def run_multi_step(user_prompt: str, user: Dict[str, Any], trace_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute a multi-step prompt with the LangChain agent and return a summary.

    Returns a dict {"trace_id":..., "summary":..., "logs": [...]}
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    # Reset per-run logs
    oc_tools.clear_action_logs()

    enable_lang = os.getenv("ENABLE_LANGCHAIN", "false").lower() == "true"
    # If LangChain is explicitly enabled but not available, fall back safely.
    if enable_lang and not LANGCHAIN_AVAILABLE:
        print("ENABLE_LANGCHAIN is true but LangChain package is not installed in the container. Falling back to safe deterministic flow.")
        enable_lang = False

    if not enable_lang:
        # fallback: very small decomposer using Ollama (or a simple rule)
        # For backward compatibility we keep a simple classifier
        intent = classify_intent_with_ai(user_prompt)
        # Very simple flow: if contains 'restart' try to authorize/execute, otherwise say hello or query
        if "restart" in user_prompt.lower() or intent == "restart_service":
            # call authorize -> evaluate risk -> approve -> execute_action -> audit
            oc_tools.authorize_tool(json.dumps({"user": user, "action": "restart_service", "trace_id": trace_id}))
            risk = oc_tools.evaluate_risk_tool(json.dumps({"user": user, "action": "restart_service", "trace_id": trace_id}))
            # attempt approval if needed
            try:
                risk_obj = json.loads(risk)
            except Exception:
                risk_obj = {}
            if risk_obj.get("requires_approval"):
                oc_tools.approve_tool(json.dumps({"user": user, "action": "restart_service", "approved": user.get("role") == "admin", "trace_id": trace_id}))
            oc_tools.execute_action_tool(json.dumps({"user": user, "action": "restart_service", "trace_id": trace_id}))
        # Minimal deterministic fallback: do not produce conversational replies.
        # Fallback only performs/attempts actions and returns an action-only summary.
        logs = oc_tools.get_action_logs()
        summary = _summarize_action_logs(logs, user, agent_message=None)
        # Indicate fallback mode in the response so callers can render appropriately.
        return {"trace_id": trace_id, "summary": summary, "logs": logs, "fallback_mode": True}

    # Build and run LangChain agent
    agent = _build_agent()
    instruction = oc_prompt.build_agent_prompt(user_prompt, user, trace_id)

    try:
        agent_output = agent.run(instruction)
    except Exception as e:
        # If agent fails, still return logs we have and an error message
        logs = oc_tools.get_action_logs()
        summary = _summarize_action_logs(logs, user, agent_message=None)
        return {"trace_id": trace_id, "summary": f"Agent failed: {e}. Partial result: {summary}", "logs": logs}

    logs = oc_tools.get_action_logs()
    # The agent_output may contain user-facing text (greeting/confirmation). Prefer it as the natural reply.
    summary = _summarize_action_logs(logs, user, agent_message=(agent_output if isinstance(agent_output, str) else None))
    return {"trace_id": trace_id, "summary": summary, "logs": logs}

