from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_evaluate_and_approve():
    ev = client.post('/evaluate', json={"user": {"user_id": "bob", "role": "operator"}, "action": "restart_service"})
    assert ev.status_code == 200
    data = ev.json()
    assert 'risk_score' in data

    ap = client.post('/approve', json={"user": {"user_id": "alice", "role": "admin"}, "action": "restart_service", "approved": True})
    assert ap.status_code == 200
    assert ap.json().get('approved') is True
