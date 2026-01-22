from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_secret_path_denied():
    res = client.post('/check_path', json={"user": {"user_id": "bob", "role": "operator"}, "path": "/etc/.env"})
    assert res.status_code == 200
    assert res.json().get('allowed') is False


def test_secret_path_allowed():
    res = client.post('/check_path', json={"user": {"user_id": "alice", "role": "admin"}, "path": "/var/log/app.log"})
    assert res.status_code == 200
    assert res.json().get('allowed') is True
