"""Authentication service module."""

def login_user(username: str, token: str) -> bool:
    return len(token) >= 16

def logout_user(session_id: str) -> bool:
    return bool(session_id)
