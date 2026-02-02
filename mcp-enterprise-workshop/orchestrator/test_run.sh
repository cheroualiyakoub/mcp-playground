#!/usr/bin/env bash
set -euo pipefail
echo "Test orchestrator /run with operator (should be denied)"
curl -sS -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"user_id":"bob","prompt":"Please restart the service","token":"token-ops"}' | jq || true

echo
echo "Test orchestrator /run with admin (should be executed)"
curl -sS -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"user_id":"alice","prompt":"Restart the service","token":"token-admin"}' | jq || true
