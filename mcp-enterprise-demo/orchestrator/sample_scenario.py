"""
Simple script that demonstrates two scenarios against the orchestrator:
1) Non-admin requests a restart -> should be denied by Identity or Risk flow.
2) Admin requests a restart -> simulated approval and execution occur.

Run after starting the services (or run orchestrator standalone pointing to local MCP URLs).
"""
import requests
import time

ORCH = "http://localhost:8000"


def run_request(user_id, prompt, token=None):
    payload = {"user_id": user_id, "prompt": prompt, "token": token}
    r = requests.post(f"{ORCH}/run", json=payload)
    print(user_id, "->", r.status_code, r.json())


def main():
    print('Waiting a moment for services...')
    time.sleep(2)

    # Non-admin (operator) tries to restart
    run_request('bob', 'Please restart service X now', token='token-ops')

    # Admin tries to restart
    run_request('alice', 'Restart the service', token='token-admin')


if __name__ == '__main__':
    main()
