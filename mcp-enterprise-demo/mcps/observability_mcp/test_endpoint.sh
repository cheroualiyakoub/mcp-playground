#!/usr/bin/env bash
set -euo pipefail
echo "POST /query (observability)"
curl -sS -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"eve","role":"viewer"}, "action":"query", "trace_id":"obs-1"}' | jq || true
