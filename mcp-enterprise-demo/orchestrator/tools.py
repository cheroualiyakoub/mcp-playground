import json
import os
import requests
from typing import Dict


def _post(url: str, path: str, payload: Dict):
    r = requests.post(f"{url}{path}", json=payload, timeout=8)
    r.raise_for_status()
    return r.json()


def authorize_tool(input_str: str) -> str:
    data = json.loads(input_str)
    id_url = os.getenv("IDENTITY_MCP_URL", "http://identity:8001")
    return json.dumps(_post(id_url, "/authorize", data))


def evaluate_risk_tool(input_str: str) -> str:
    data = json.loads(input_str)
    risk_url = os.getenv("RISK_MCP_URL", "http://risk:8004")
    return json.dumps(_post(risk_url, "/evaluate", data))


def approve_tool(input_str: str) -> str:
    data = json.loads(input_str)
    risk_url = os.getenv("RISK_MCP_URL", "http://risk:8004")
    return json.dumps(_post(risk_url, "/approve", data))


def execute_action_tool(input_str: str) -> str:
    data = json.loads(input_str)
    # enforce authorization by calling identity before execution
    id_url = os.getenv("IDENTITY_MCP_URL", "http://identity:8001")
    auth = _post(id_url, "/authorize", {"user": data.get("user"), "action": data.get("action"), "trace_id": data.get("trace_id")})
    if not auth.get("allowed"):
        return json.dumps({"error": "not_authorized", "reason": auth.get("reason")})
    ops_url = os.getenv("OPERATIONS_MCP_URL", "http://operations:8002")
    return json.dumps(_post(ops_url, "/execute_action", data))


def query_observability_tool(input_str: str) -> str:
    data = json.loads(input_str)
    obs_url = os.getenv("OBSERVABILITY_MCP_URL", "http://observability:8003")
    return json.dumps(_post(obs_url, "/query", data))


def check_secret_tool(input_str: str) -> str:
    data = json.loads(input_str)
    secrets_url = os.getenv("SECRETS_MCP_URL", "http://secrets:8005")
    return json.dumps(_post(secrets_url, "/check_path", data))


def log_audit_tool(input_str: str) -> str:
    data = json.loads(input_str)
    audit_url = os.getenv("AUDIT_MCP_URL", "http://audit:8006")
    return json.dumps(_post(audit_url, "/log", data))
from typing import Dict
import os
import requests


def post_json(url: str, path: str, payload: Dict):
    r = requests.post(f"{url}{path}", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()
