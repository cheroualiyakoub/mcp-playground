#!/usr/bin/env bash
# Test Identity MCP
set -euo pipefail

echo "POST /authorize as admin (alice)"
curl -sS -X POST http://localhost:8001/authorize \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"alice","role":"admin"}, "action":"restart_service", "trace_id":"t-1"}' | jq || true

echo
echo "POST /authorize as operator (bob)"
curl -sS -X POST http://localhost:8001/authorize \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"bob","role":"operator"}, "action":"restart_service", "trace_id":"t-2"}' | jq || true
