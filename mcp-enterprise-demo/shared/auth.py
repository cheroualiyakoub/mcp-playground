from typing import Optional
import os

API_TOKENS = {
    # token: role
    "token-admin": "admin",
    "token-ops": "operator",
    "token-view": "viewer",
}


def get_role_from_token(token: Optional[str]) -> Optional[str]:
    if not token:
        return None
    return API_TOKENS.get(token)


def require_token(headers) -> Optional[str]:
    # Expect header Authorization: Bearer <token>
    auth = headers.get("authorization") or headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) != 2:
        return None
    return parts[1]
