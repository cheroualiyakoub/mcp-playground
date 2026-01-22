#!/usr/bin/env bash
set -euo pipefail
echo "POST /evaluate"
curl -sS -X POST http://localhost:8004/evaluate \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"bob","role":"operator"}, "action":"restart_service", "trace_id":"r-1"}' | jq || true

echo
echo "POST /approve (simulate admin approval)"
curl -sS -X POST http://localhost:8004/approve \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"alice","role":"admin"}, "action":"restart_service", "approved": true, "trace_id":"r-1"}' | jq || true
