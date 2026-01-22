#!/usr/bin/env bash
set -euo pipefail
echo "GET /report"
curl -sS http://localhost:8006/report | jq || true

echo
echo "POST /log (create a test entry)"
curl -sS -X POST http://localhost:8006/log \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","action":"test_action","result":"ok","reason":"testing","trace_id":"log-1"}' | jq || true

echo
echo "GET /report (after log)"
curl -sS http://localhost:8006/report | jq || true
