FROM python:3.9-slim
WORKDIR /app
# When building from repo root, copy files from the orchestrator subfolder
# Copy shared utilities used across services
FROM python:3.10-slim
WORKDIR /app
COPY orchestrator/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy orchestrator package and shared utilities
COPY orchestrator ./orchestrator
COPY shared ./shared

ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "orchestrator.agent:app", "--host", "0.0.0.0", "--port", "8000"]
