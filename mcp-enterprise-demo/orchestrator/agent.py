from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import uuid
import json
from typing import Optional

app = FastAPI(title="MCP Orchestrator (AI-powered)")


class PromptIn(BaseModel):
    user_id: str
    prompt: str
    token: Optional[str] = None


def call_mcp(url: str, path: str, payload: dict):
    try:
        r = requests.post(f"{url}{path}", json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MCP call failed: {str(e)}")


# -------------------------
# AI Intent Classification
# -------------------------

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


def classify_intent_with_ai(prompt: str) -> str:
    """
    Uses an LLM to classify the user prompt into one of the allowed actions.
    If the AI fails, return 'unknown' (safe default).
    """

    system_prompt = """
You are an AI orchestrator in a secure enterprise system.

Your task:
Classify the user request into ONE of the following actions:

- restart_service (high risk)
- query (read-only, safe)
- forbidden (security-sensitive or malicious)
- unknown

Rules:
- If the user asks to restart, stop, modify, or execute infrastructure -> restart_service
- If the user asks to read logs, metrics, or status -> query
- If the user asks for secrets, tokens, env files, credentials -> forbidden
- If unclear -> unknown

Return STRICT JSON:
{"action": "<one_of_the_above>"}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=15)
        r.raise_for_status()
        content = r.json().get("message", {}).get("content")
        if not content:
            return "unknown"
        parsed = json.loads(content)
        return parsed.get("action", "unknown")

    except Exception as e:
        # FAIL SAFE: never allow dangerous actions on AI failure
        print("AI failure, defaulting to unknown:", e)
        return "unknown"


@app.post("/run")
def run_prompt(p: PromptIn):
    trace_id = str(uuid.uuid4())

    # Fake auth mapping (demo only)
    user = {
        "user_id": p.user_id,
        "role": "admin" if p.token == "admin-token" else "user"
    }

    # 1️⃣ AI decides intent
    action = classify_intent_with_ai(p.prompt)

    # 2️⃣ Identity / Policy MCP
    id_url = os.getenv("IDENTITY_MCP_URL", "http://localhost:8001")
    id_resp = call_mcp(
        id_url,
        "/authorize",
        {
            "user": user,
            "action": action,
            "trace_id": trace_id
        }
    )

    if not id_resp.get("allowed"):
        audit_url = os.getenv("AUDIT_MCP_URL", "http://localhost:8006")
        call_mcp(
            audit_url,
            "/log",
            {
                "user_id": user["user_id"],
                "action": action,
                "result": "denied",
                "reason": id_resp.get("reason"),
                "trace_id": trace_id
            }
        )
        return {
            "status": "denied",
            "reason": id_resp.get("reason"),
            "trace_id": trace_id
        }

    # 3️⃣ High-risk flow
    if action == "restart_service":
        risk_url = os.getenv("RISK_MCP_URL", "http://localhost:8004")
        risk = call_mcp(
            risk_url,
            "/evaluate",
            {
                "user": user,
                "action": action,
                "trace_id": trace_id
            }
        )

        if risk.get("requires_approval"):
            approved = user["role"] == "admin"

            approval = call_mcp(
                risk_url,
                "/approve",
                {
                    "user": user,
                    "action": action,
                    "approved": approved,
                    "trace_id": trace_id
                }
            )

            if not approval.get("approved"):
                call_mcp(
                    os.getenv("AUDIT_MCP_URL", "http://localhost:8006"),
                    "/log",
                    {
                        "user_id": user["user_id"],
                        "action": action,
                        "result": "denied",
                        "reason": "human approval required",
                        "trace_id": trace_id
                    }
                )
                return {
                    "status": "requires_approval",
                    "approved": False,
                    "trace_id": trace_id
                }

        ops_url = os.getenv("OPERATIONS_MCP_URL", "http://localhost:8002")
        result = call_mcp(
            ops_url,
            "/execute_action",
            {
                "user": user,
                "action": action,
                "trace_id": trace_id
            }
        )

        call_mcp(
            os.getenv("AUDIT_MCP_URL", "http://localhost:8006"),
            "/log",
            {
                "user_id": user["user_id"],
                "action": action,
                "result": "executed",
                "reason": "approved",
                "trace_id": trace_id
            }
        )

        return {
            "status": "executed",
            "details": result,
            "trace_id": trace_id
        }

    # 4️⃣ Read-only flow
    obs_url = os.getenv("OBSERVABILITY_MCP_URL", "http://localhost:8003")
    obs = call_mcp(
        obs_url,
        "/query",
        {
            "user": user,
            "action": action,
            "trace_id": trace_id
        }
    )

    call_mcp(
        os.getenv("AUDIT_MCP_URL", "http://localhost:8006"),
        "/log",
        {
            "user_id": user["user_id"],
            "action": action,
            "result": "ok",
            "reason": "read-only query",
            "trace_id": trace_id
        }
    )

    return {
        "status": "ok",
        "result": obs,
        "trace_id": trace_id
    }
