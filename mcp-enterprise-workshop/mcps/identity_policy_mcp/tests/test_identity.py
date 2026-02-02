from fastapi.testclient import TestClient
from server import app


client = TestClient(app)


def test_authorize_admin():
    res = client.post('/authorize', json={"user": {"user_id": "alice", "role": "admin"}, "action": "restart_service"})
    assert res.status_code == 200
    assert res.json().get('allowed') is True


def test_authorize_non_admin():
    res = client.post('/authorize', json={"user": {"user_id": "bob", "role": "operator"}, "action": "restart_service"})
    assert res.status_code == 200
    assert res.json().get('allowed') is False
