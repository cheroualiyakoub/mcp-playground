Operations MCP

Role: execute high-risk actions (restart service, DB writes). This MCP requires approval and admin role.

Endpoints:
- POST /execute_action { user, action, trace_id } -> { result, reason }

Baseline: operations are simulated. Only `admin` role allowed to perform operations.

Run:
```
pip install -r requirements.txt
uvicorn server:app --reload --port 8002
```
