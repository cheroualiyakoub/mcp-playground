Orchestrator

Simple FastAPI app that accepts user prompts and routes to MCPs via HTTP. Endpoint:

- POST /run { user_id, prompt, token }

The orchestrator uses environment variables to locate MCPs (see docker-compose.yml). It will call Identity -> Risk -> Operations -> Audit / Observability as needed.

Run locally:

```bash
pip install -r requirements.txt
uvicorn agent:app --reload --port 8000
```
