from typing import Dict
import os
import requests


def post_json(url: str, path: str, payload: Dict):
    r = requests.post(f"{url}{path}", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()
