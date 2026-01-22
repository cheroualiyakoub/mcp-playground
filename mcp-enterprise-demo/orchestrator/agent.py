from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from shared.schemas.common import ActionRequest, ActionResponse, User
from shared.auth import require_token, get_role_from_token
import uuid

app = FastAPI(title="MCP Orchestrator")


class PromptIn(BaseModel):
    user_id: str
    prompt: str
    token: str = None


def call_mcp(url: str, path: str, payload: dict):
    try:
        r = requests.post(f"{url}{path}", json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/run")
def run_prompt(p: PromptIn):
    trace_id = str(uuid.uuid4())

    user = {"user_id": p.user_id, "role": get_role_from_token(p.token) or 'unknown'}

    # naive intent parsing: if prompt contains restart -> restart service
    if "restart" in p.prompt.lower() or "restart service" in p.prompt.lower():
        action = "restart_service"
    else:
        action = "query"

    # Step 1: ask Identity MCP
    id_url = os.getenv("IDENTITY_MCP_URL", "http://localhost:8001")
    id_resp = call_mcp(id_url, "/authorize", {"user": user, "action": action, "trace_id": trace_id})

    if not id_resp.get("allowed"):
        # log denial via audit MCP
        audit_url = os.getenv("AUDIT_MCP_URL", "http://localhost:8006")
        try:
            call_mcp(audit_url, "/log", {"user_id": p.user_id, "action": action, "result": "denied", "reason": id_resp.get("reason"), "trace_id": trace_id})
        except:
            pass
        return {"status": "denied", "reason": id_resp.get("reason")}

    # If action is high-risk, route to Risk MCP
    if action == "restart_service":
        risk_url = os.getenv("RISK_MCP_URL", "http://localhost:8004")
        risk = call_mcp(risk_url, "/evaluate", {"user": user, "action": action, "trace_id": trace_id})
        if risk.get("requires_approval"):
            # Baseline: simulate human-in-the-loop. Auto-approve if requester is admin, else require human.
            approved_flag = True if user.get("role") == "admin" else False
            approve = call_mcp(risk_url, "/approve", {"user": user, "action": action, "approved": approved_flag, "trace_id": trace_id})
            if not approve.get("approved"):
                # approval denied; log and return
                call_mcp(os.getenv("AUDIT_MCP_URL", "http://localhost:8006"), "/log", {"user_id": p.user_id, "action": action, "result": "denied", "reason": approve.get("reason", "not approved"), "trace_id": trace_id})
                return {"status": "requires_approval", "approved": False, "reason": approve.get("reason")}
            # else approved True -> continue to execution

        # approved; call operations MCP to execute
        ops_url = os.getenv("OPERATIONS_MCP_URL", "http://localhost:8002")
        exec_resp = call_mcp(ops_url, "/execute_action", {"user": user, "action": action, "trace_id": trace_id})
        # log outcome
        call_mcp(os.getenv("AUDIT_MCP_URL", "http://localhost:8006"), "/log", {"user_id": p.user_id, "action": action, "result": exec_resp.get("result", "unknown"), "reason": exec_resp.get("reason"), "trace_id": trace_id})
        return {"status": "executed", "details": exec_resp}

    # default: query flow - observability
    obs_url = os.getenv("OBSERVABILITY_MCP_URL", "http://localhost:8003")
    obs = call_mcp(obs_url, "/query", {"user": user, "action": action, "trace_id": trace_id})
    call_mcp(os.getenv("AUDIT_MCP_URL", "http://localhost:8006"), "/log", {"user_id": p.user_id, "action": action, "result": "ok", "reason": "queried observability", "trace_id": trace_id})
    return {"status": "ok", "result": obs}
