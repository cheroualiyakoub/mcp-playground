from fastapi import FastAPI
from pydantic import BaseModel
import os
import sqlite3
import datetime

app = FastAPI(title="Audit & Reporting MCP")


class LogIn(BaseModel):
    user_id: str
    action: str
    result: str
    reason: str = None
    trace_id: str = None


@app.post("/log")
def log_entry(payload: LogIn):
    db = os.getenv('AUDIT_DB_PATH', '/data/audit.db')
    conn = sqlite3.connect(db)
    c = conn.cursor()
    # Ensure table exists (idempotent). This makes the MCP resilient in fresh environments.
    c.execute('''
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_id TEXT,
        action TEXT,
        result TEXT,
        reason TEXT,
        trace_id TEXT
    )
    ''')
    c.execute('INSERT INTO audit(timestamp, user_id, action, result, reason, trace_id) VALUES (?,?,?,?,?,?)',
              (datetime.datetime.utcnow().isoformat(), payload.user_id, payload.action, payload.result, payload.reason, payload.trace_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}


@app.get("/report")
def report():
    db = os.getenv('AUDIT_DB_PATH', '/data/audit.db')
    conn = sqlite3.connect(db)
    c = conn.cursor()
    try:
        c.execute('SELECT id, timestamp, user_id, action, result FROM audit ORDER BY id DESC LIMIT 100')
        rows = c.fetchall()
    except Exception:
        rows = []
    conn.close()
    return {"rows": [dict(id=r[0], timestamp=r[1], user_id=r[2], action=r[3], result=r[4]) for r in rows]}
