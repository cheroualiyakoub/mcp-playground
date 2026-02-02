#!/usr/bin/env bash
set -euo pipefail
echo "POST /execute_action as admin"
curl -sS -X POST http://localhost:8002/execute_action \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"alice","role":"admin"}, "action":"restart_service", "trace_id":"op-1"}' | jq || true

echo
echo "POST /execute_action as operator (should be denied)"
curl -sS -X POST http://localhost:8002/execute_action \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"bob","role":"operator"}, "action":"restart_service", "trace_id":"op-2"}' | jq || true
