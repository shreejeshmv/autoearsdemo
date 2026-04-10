"""User Service – models, helpers, and Flask application."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from flask import Flask, Response, jsonify, request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TASK_SERVICE_URL = "http://localhost:5001"

# ---------------------------------------------------------------------------
# Database layer (in-memory)
# ---------------------------------------------------------------------------

_users: Dict[str, Dict[str, Any]] = {}


def _utc_now() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------


def create_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user and store it."""
    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        raise ValueError("name is required and must be a non-empty string.")

    email = data.get("email")
    if not email or not isinstance(email, str) or not email.strip():
        raise ValueError("email is required and must be a non-empty string.")

    now = _utc_now()
    user_id = str(uuid.uuid4())
    user: Dict[str, Any] = {
        "id": user_id,
        "name": name.strip(),
        "email": email.strip(),
        "created_at": now,
    }
    _users[user_id] = user
    return user


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user by ID."""
    return _users.get(user_id)


def list_users() -> List[Dict[str, Any]]:
    """Return all users."""
    return list(_users.values())


def update_user(user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing user. Returns ``None`` if not found."""
    user = _users.get(user_id)
    if user is None:
        return None

    if "name" in data:
        name = data["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string.")
        user["name"] = name.strip()

    if "email" in data:
        email = data["email"]
        if not isinstance(email, str) or not email.strip():
            raise ValueError("email must be a non-empty string.")
        user["email"] = email.strip()

    return user


def delete_user(user_id: str) -> bool:
    """Delete a user. Returns ``True`` if the user existed."""
    return _users.pop(user_id, None) is not None


def reset_users() -> None:
    """Clear all users (used in tests)."""
    _users.clear()


def fetch_user_tasks(
    user_id: str,
    overdue_only: bool = False,
    base_url: str = TASK_SERVICE_URL,
) -> List[Dict[str, Any]]:
    """Fetch tasks assigned to a user from the Task Service.

    Args:
        user_id: The user whose tasks to fetch.
        overdue_only: If ``True`` append ``?overdue=true`` to the request.
        base_url: Root URL of the task service.

    Returns:
        A list of task dicts.

    Raises:
        requests.RequestException: On network / HTTP errors.
    """
    params: Dict[str, str] = {"assignee_id": user_id}
    if overdue_only:
        params["overdue"] = "true"
    resp = requests.get(f"{base_url}/tasks", params=params, timeout=5)
    resp.raise_for_status()
    return resp.json()  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------


def create_app() -> Flask:
    """Application factory for the User Service."""
    app = Flask(__name__)

    @app.route("/users", methods=["GET"])
    def handle_list_users() -> tuple[Response, int]:
        return jsonify(list_users()), 200

    @app.route("/users", methods=["POST"])
    def handle_create_user() -> tuple[Response, int]:
        data = request.get_json(silent=True) or {}
        try:
            user = create_user(data)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(user), 201

    @app.route("/users/<user_id>", methods=["GET"])
    def handle_get_user(user_id: str) -> tuple[Response, int]:
        user = get_user(user_id)
        if user is None:
            return jsonify({"error": "User not found."}), 404
        return jsonify(user), 200

    @app.route("/users/<user_id>", methods=["PUT"])
    def handle_update_user(user_id: str) -> tuple[Response, int]:
        data = request.get_json(silent=True) or {}
        try:
            user = update_user(user_id, data)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        if user is None:
            return jsonify({"error": "User not found."}), 404
        return jsonify(user), 200

    @app.route("/users/<user_id>", methods=["DELETE"])
    def handle_delete_user(user_id: str) -> tuple[Response, int]:
        if delete_user(user_id):
            return jsonify({"message": "User deleted."}), 200
        return jsonify({"error": "User not found."}), 404

    @app.route("/users/<user_id>/tasks", methods=["GET"])
    def handle_user_tasks(user_id: str) -> tuple[Response, int]:
        user = get_user(user_id)
        if user is None:
            return jsonify({"error": "User not found."}), 404
        overdue_param = request.args.get("overdue", "").lower()
        overdue_only = overdue_param == "true"
        try:
            tasks = fetch_user_tasks(user_id, overdue_only=overdue_only)
        except requests.RequestException as exc:
            return jsonify({"error": f"Task service unavailable: {exc}"}), 502
        return jsonify(tasks), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
