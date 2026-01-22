from fastapi import FastAPI
from pydantic import BaseModel
import random
import os
import requests

app = FastAPI(title="Risk & Approval MCP")


class EvalIn(BaseModel):
    user: dict
    action: str
    trace_id: str = None


@app.post("/evaluate")
def evaluate(payload: EvalIn):
    # Very naive risk scoring
    score = random.randint(1, 100)
    requires = score > 50
    return {"risk_score": score, "requires_approval": requires}


class ApproveIn(BaseModel):
    user: dict
    action: str
    approved: bool = False
    trace_id: str = None


@app.post("/approve")
def approve(incoming: ApproveIn):
    # Simulate human-in-the-loop: baseline auto-deny unless approved True
    if incoming.approved:
        return {"approved": True}
    return {"approved": False, "reason": "approval required from human approver"}
