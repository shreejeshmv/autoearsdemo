"""In-memory data store for users."""

from typing import Any, Dict, Optional
import uuid


# In-memory user storage: user_id -> user dict
_users: Dict[str, Dict[str, Any]] = {}


def get_all_users() -> list[Dict[str, Any]]:
    """Return all users."""
    return list(_users.values())


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Return a single user by ID, or None if not found."""
    return _users.get(user_id)


def create_user(name: str, email: str = "") -> Dict[str, Any]:
    """Create a new user and store it.

    Args:
        name: The user's name.
        email: The user's email.

    Returns:
        The created user dictionary.
    """
    user_id = str(uuid.uuid4())
    user: Dict[str, Any] = {
        "id": user_id,
        "name": name,
        "email": email,
    }
    _users[user_id] = user
    return user


def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing user.

    Args:
        user_id: The ID of the user to update.
        updates: A dictionary of fields to update.

    Returns:
        The updated user dictionary, or None if not found.
    """
    user = _users.get(user_id)
    if user is None:
        return None
    allowed_fields = {"name", "email"}
    for key, value in updates.items():
        if key in allowed_fields:
            user[key] = value
    return user


def delete_user(user_id: str) -> bool:
    """Delete a user by ID.

    Returns:
        True if the user was deleted, False if not found.
    """
    if user_id in _users:
        del _users[user_id]
        return True
    return False


def clear_all() -> None:
    """Remove all users (used for testing)."""
    _users.clear()
