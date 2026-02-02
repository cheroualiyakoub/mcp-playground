from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    user_id: str
    role: str


class ActionRequest(BaseModel):
    user: User
    action: str
    payload: Optional[dict] = None
    trace_id: Optional[str] = None


class ActionResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    data: Optional[dict] = None


class AuditEntry(BaseModel):
    timestamp: datetime
    user_id: str
    action: str
    result: str
    reason: Optional[str]
    trace_id: Optional[str]
