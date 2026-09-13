"""
CampusHelp - Phase 6: Authentication & Role Handling
---------------------------------------------------------
Minimal login system for two roles: Admin and User. Not meant to be
production-grade security — this is a student/demo project, so credentials
are stored in a simple local file rather than a real user database or
hashing service. Good enough to gate the upload feature behind a role check.

Usage:
    from auth import authenticate, Role
    result = authenticate(username, password)
"""

import json
from pathlib import Path
from enum import Enum

# ---------- Config ----------
USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


# ---------- Default users (created on first run if users.json is missing) ----------
DEFAULT_USERS = {
    "admin": {"password": "admin123", "role": Role.ADMIN.value},
    "student": {"password": "student123", "role": Role.USER.value},
}


def _ensure_users_file():
    """Create data/users.json with default accounts if it doesn't exist yet."""
    if not USERS_FILE.exists():
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_USERS, f, indent=2)


def _load_users() -> dict:
    _ensure_users_file()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Public API ----------
def authenticate(username: str, password: str) -> dict:
    """
    Check a username/password pair against stored users.

    Returns:
        {"success": bool, "username": str, "role": str | None, "message": str}
    """
    if not username or not password:
        return {
            "success": False,
            "username": username,
            "role": None,
            "message": "Username and password are required.",
        }

    users = _load_users()
    user = users.get(username)

    if not user or user["password"] != password:
        return {
            "success": False,
            "username": username,
            "role": None,
            "message": "Invalid username or password.",
        }

    return {
        "success": True,
        "username": username,
        "role": user["role"],
        "message": f"Welcome, {username}.",
    }


def is_admin(role: str) -> bool:
    """Convenience check used before allowing access to upload features."""
    return role == Role.ADMIN.value


def is_user(role: str) -> bool:
    return role == Role.USER.value


# ---------- Standalone test ----------
if __name__ == "__main__":
    print("Testing default accounts:\n")
    for username in ("admin", "student", "nonexistent"):
        result = authenticate(username, "admin123" if username == "admin" else "student123")
        print(f"{username}: {result}")