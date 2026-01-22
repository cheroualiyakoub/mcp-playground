#!/usr/bin/env bash
set -euo pipefail
# Query the audit SQLite DB from inside the running audit container using Python (no host installs required)
echo "Querying audit DB inside audit container..."
docker exec -i audit python3 - <<'PY'
import sqlite3, json
db='/data/audit.db'
try:
    conn=sqlite3.connect(db)
    c=conn.cursor()
    rows=c.execute('SELECT id,timestamp,user_id,action,result,reason,trace_id FROM audit ORDER BY id DESC LIMIT 50').fetchall()
    for r in rows:
        print(json.dumps({'id':r[0],'timestamp':r[1],'user_id':r[2],'action':r[3],'result':r[4],'reason':r[5],'trace_id':r[6]}))
    conn.close()
except Exception as e:
    print('ERROR', e)
    raise
PY
