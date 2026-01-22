#!/usr/bin/env bash
set -euo pipefail
echo "POST /check_path with sensitive path (should be denied)"
curl -sS -X POST http://localhost:8005/check_path \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"bob","role":"operator"}, "path":"/etc/.env", "trace_id":"s-1"}' | jq || true

echo
echo "POST /check_path with safe path"
curl -sS -X POST http://localhost:8005/check_path \
  -H "Content-Type: application/json" \
  -d '{"user": {"user_id":"alice","role":"admin"}, "path":"/var/log/app.log", "trace_id":"s-2"}' | jq || true
