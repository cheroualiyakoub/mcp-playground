from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Secrets & Security MCP")


class CheckIn(BaseModel):
    user: dict
    path: str
    trace_id: str = None


@app.post("/check_path")
def check_path(payload: CheckIn):
    patterns = os.getenv('SENSITIVE_PATTERNS', '.env,SECRET,TOKEN,KEY,cert')
    for p in patterns.split(','):
        if p and p in payload.path:
            return {"allowed": False, "reason": f"path contains sensitive pattern: {p}"}
    return {"allowed": True}
