FROM python:3.10-slim
WORKDIR /app

# copy and install dependencies
COPY orchestrator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy orchestrator package and shared utilities
COPY orchestrator ./orchestrator
COPY shared ./shared

ENV PORT=8000
EXPOSE 8000
# Run the FastAPI server implemented in orchestrator/server.py
CMD ["uvicorn", "orchestrator.server:app", "--host", "0.0.0.0", "--port", "8000"]
