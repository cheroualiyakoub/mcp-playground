from fastapi import FastAPI
from pydantic import BaseModel
import os
import sqlite3
from typing import Dict

app = FastAPI(title="Observability MCP")


class QueryIn(BaseModel):
    user: Dict
    action: str
    trace_id: str = None


@app.post("/query")
def query(payload: QueryIn):
    # Read-only access to audit DB
    db = os.getenv("AUDIT_DB_PATH", "/data/audit.db")
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        # If audit table missing, return empty rows rather than raising
        try:
            c.execute('SELECT id, timestamp, user_id, action, result FROM audit ORDER BY id DESC LIMIT 20')
            rows = c.fetchall()
        except Exception:
            rows = []
        conn.close()
        return {"rows": [dict(id=r[0], timestamp=r[1], user_id=r[2], action=r[3], result=r[4]) for r in rows]}
    except Exception as e:
        return {"error": str(e)}
