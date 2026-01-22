from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_query_returns_rows():
    res = client.post('/query', json={"user": {"user_id": "eve", "role": "viewer"}, "action": "query"})
    assert res.status_code == 200
    assert isinstance(res.json(), dict)
