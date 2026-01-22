from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import sqlite3
from pathlib import Path
from shared.schemas.common import ActionRequest, ActionResponse
from shared.auth import get_role_from_token, require_token
from shared.errors import forbidden

app = FastAPI(title="Identity & Policy MCP")


class AuthorizeIn(BaseModel):
    user: dict
    action: str
    trace_id: str = None


@app.post("/authorize")
def authorize(payload: AuthorizeIn, request: Request):
    # This MCP enforces policies based on Operational DB
    db_path = os.getenv("DB_PATH", "/data/operational.db")
    user = payload.user
    # simple policy: only admin can restart_service
    if payload.action == 'restart_service':
        if user.get('role') == 'admin':
            return {"allowed": True}
        else:
            return {"allowed": False, "reason": "only admin may perform restart_service"}

    # default allow for queries
    return {"allowed": True}
