from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid

from orchestrator import agent


app = FastAPI(title="MCP Orchestrator (Server)")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for workshop/development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptIn(BaseModel):
    user_id: str
    prompt: str
    token: Optional[str] = None


@app.post("/run")
def run_prompt(p: PromptIn):
    trace_id = str(uuid.uuid4())

    # Simple role mapping for demo: token 'admin-token' => admin
    user = {"user_id": p.user_id, "role": "admin" if p.token == "admin-token" else "user"}

    try:
        result = agent.run_multi_step(p.prompt, user, trace_id)
        return {"trace_id": result.get("trace_id"), "summary": result.get("summary"), "logs": result.get("logs")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
