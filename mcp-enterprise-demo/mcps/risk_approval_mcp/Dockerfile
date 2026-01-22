FROM python:3.9-slim
WORKDIR /app
COPY mcps/risk_approval_mcp/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY mcps/risk_approval_mcp/. .
COPY shared/ ./shared
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8004"]
