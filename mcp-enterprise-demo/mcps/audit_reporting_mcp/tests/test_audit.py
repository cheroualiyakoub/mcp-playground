import os
from fastapi.testclient import TestClient
import sqlite3

# Ensure audit server uses an in-memory DB for tests
os.environ['AUDIT_DB_PATH'] = ':memory:'

from server import app

client = TestClient(app)


def test_log_and_report():
    # log an entry
    res = client.post('/log', json={"user_id": "alice", "action": "test_action", "result": "ok", "reason": "test", "trace_id": "t1"})
    assert res.status_code == 200
    assert res.json().get('status') == 'ok'

    # report should include at least one row
    rep = client.get('/report')
    assert rep.status_code == 200
    data = rep.json()
    assert 'rows' in data
