Observability MCP

Role: provide read-only access to logs/metrics. Uses the Audit DB as a data source.

Endpoints:
- POST /query { user, action, trace_id } -> { rows: [...] }

Run:
```
pip install -r requirements.txt
uvicorn server:app --reload --port 8003
```
