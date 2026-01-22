FROM python:3.9-slim
WORKDIR /app
# When building from repo root, copy files from the orchestrator subfolder
COPY orchestrator/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY orchestrator/. .
# Copy shared utilities used across services
COPY shared/ ./shared
CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8000"]
