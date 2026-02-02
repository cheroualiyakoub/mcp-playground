Identity & Policy MCP

Role: handle authentication & authorization. Exposes:
- POST /authorize {user, action, trace_id} -> returns {allowed: bool, reason: str}

Baseline policy: only users with role 'admin' can perform restart_service. All other queries allowed.

Run locally for testing:
  pip install -r requirements.txt
  uvicorn server:app --reload --port 8001
