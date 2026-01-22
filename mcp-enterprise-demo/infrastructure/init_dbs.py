"""
Initialize operational and audit SQLite databases with baseline schema and seed data.
Run this script before starting services (docker-compose will also mount /data where these files should live).
"""
import sqlite3
from pathlib import Path
import datetime

DATA_DIR = Path(__file__).parent
OP_DB = DATA_DIR / "operational.db"
AUDIT_DB = DATA_DIR / "audit.db"


def init_operational():
    conn = sqlite3.connect(OP_DB)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        user_id TEXT PRIMARY KEY,
        role TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS services (
        name TEXT PRIMARY KEY,
        metadata TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS risk_thresholds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        threshold INTEGER
    )
    ''')

    # seed
    c.execute('INSERT OR REPLACE INTO roles(user_id, role) VALUES (?,?)', ('alice', 'admin'))
    c.execute('INSERT OR REPLACE INTO roles(user_id, role) VALUES (?,?)', ('bob', 'operator'))
    c.execute('INSERT OR REPLACE INTO roles(user_id, role) VALUES (?,?)', ('eve', 'viewer'))
    c.execute('INSERT OR REPLACE INTO risk_thresholds(action, threshold) VALUES (?,?)', ('restart_service', 70))

    conn.commit()
    conn.close()


def init_audit():
    conn = sqlite3.connect(AUDIT_DB)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_id TEXT,
        action TEXT,
        result TEXT,
        reason TEXT,
        trace_id TEXT
    )
    ''')

    # sample row
    c.execute('INSERT INTO audit(timestamp, user_id, action, result, reason, trace_id) VALUES (?,?,?,?,?,?)',
              (datetime.datetime.utcnow().isoformat(), 'system', 'init', 'ok', 'seeded', 'init-1'))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    print('Initializing databases in', DATA_DIR)
    init_operational()
    init_audit()
    print('Done')
