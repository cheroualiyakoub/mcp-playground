MCP Enterprise Demo

This repository is a baseline demo for an orchestrator + multiple MCP microservices pattern.

Architecture:
- Orchestrator (FastAPI) routes user prompts to MCPs and aggregates results.
- MCPs are small FastAPI microservices providing policy, risk/approval, operations, secrets protections, observability and audit/reporting.
- Orchestrator never accesses DBs directly; it calls MCPs over HTTP.

Quick start:
1. Initialize SQLite DBs (creates `infrastructure/operational.db` and `infrastructure/audit.db`):

```bash
python3 infrastructure/init_dbs.py
```

2. Build and start services with Docker Compose:

```bash
docker compose up --build
```

3. (Optional) Run the sample scenario after services are up:

```bash
python3 orchestrator/sample_scenario.py
```

Notes:
- Each MCP folder contains a `requirements.txt`, `Dockerfile`, `server.py`, and basic unit tests under `tests/`.
- The orchestrator exposes POST /run to submit prompts.
