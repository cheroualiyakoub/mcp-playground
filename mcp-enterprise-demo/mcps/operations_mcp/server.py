from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI(title="Operations MCP")


class ExecIn(BaseModel):
    user: dict
    action: str
    trace_id: str = None


@app.post("/execute_action")
def execute(payload: ExecIn):
    # Operations MCP enforces approval; default deny unless approved flag is present in payload
    # Baseline: no real side-effects; simulate execution
    # Expect payload to contain 'approved': True to execute
    if payload.user.get('role') != 'admin':
        return {"result": "denied", "reason": "only admin may execute operations"}

    # simulate action
    if payload.action == 'restart_service':
        return {"result": "ok", "reason": "service restarted (simulated)"}

    return {"result": "ok", "reason": "action executed (simulated)"}
