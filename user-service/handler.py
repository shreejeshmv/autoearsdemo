"""Request handlers (route logic) for the user-service."""

from typing import Any, Dict, Tuple

import store


def handle_create_user(body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Handle POST /users.

    Args:
        body: Parsed JSON request body.

    Returns:
        Tuple of (response_body, status_code).
    """
    name = body.get("name")
    if not name:
        return {"error": "Field 'name' is required."}, 400
    user = store.create_user(name=name, email=body.get("email", ""))
    return user, 201


def handle_list_users() -> Tuple[Any, int]:
    """Handle GET /users."""
    return store.get_all_users(), 200


def handle_get_user(user_id: str) -> Tuple[Dict[str, Any], int]:
    """Handle GET /users/<user_id>."""
    user = store.get_user(user_id)
    if user is None:
        return {"error": "User not found."}, 404
    return user, 200


def handle_update_user(
    user_id: str, body: Dict[str, Any]
) -> Tuple[Dict[str, Any], int]:
    """Handle PUT /users/<user_id>."""
    user = store.update_user(user_id, body)
    if user is None:
        return {"error": "User not found."}, 404
    return user, 200


def handle_delete_user(user_id: str) -> Tuple[Dict[str, Any], int]:
    """Handle DELETE /users/<user_id>."""
    deleted = store.delete_user(user_id)
    if not deleted:
        return {"error": "User not found."}, 404
    return {"message": "User deleted."}, 200
