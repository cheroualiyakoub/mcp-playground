from fastapi.testclient import TestClient
import os
from server import app

client = TestClient(app)


def test_execute_admin_allowed():
    res = client.post('/execute_action', json={"user": {"user_id": "alice", "role": "admin"}, "action": "restart_service"})
    assert res.status_code == 200
    assert res.json().get('result') == 'ok'


def test_execute_non_admin_denied():
    res = client.post('/execute_action', json={"user": {"user_id": "bob", "role": "operator"}, "action": "restart_service"})
    assert res.status_code == 200
    assert res.json().get('result') == 'denied'
