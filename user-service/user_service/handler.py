"""Flask request handlers for the user-service API."""

from __future__ import annotations

from flask import Flask, Response, jsonify, request

from .models import Notification, User
from .store import NotificationStore, UserStore

app = Flask(__name__)
user_store = UserStore()
notification_store = NotificationStore()


# -- User CRUD ----------------------------------------------------------------


@app.route("/users", methods=["POST"])
def create_user() -> tuple[Response, int]:
    """Create a new user."""
    data = request.get_json(force=True)
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    user = User(name=data["name"], email=data.get("email", ""))
    user_store.create(user)
    return jsonify({"id": user.id, "name": user.name, "email": user.email}), 201


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id: str) -> tuple[Response, int]:
    """Retrieve a single user."""
    user = user_store.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"id": user.id, "name": user.name, "email": user.email}), 200


# -- Notifications ------------------------------------------------------------


@app.route("/notifications", methods=["POST"])
def create_notification() -> tuple[Response, int]:
    """Create a notification for a user (REQ-011)."""
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "request body is required"}), 400

    user_id = data.get("user_id")
    message = data.get("message")
    if not user_id or not message:
        return jsonify({"error": "user_id and message are required"}), 400

    notification = Notification(
        user_id=user_id,
        message=message,
        notification_type=data.get("notification_type", "overdue_task"),
    )
    notification_store.create(notification)
    return jsonify(notification.to_dict()), 201


@app.route("/notifications/<user_id>", methods=["GET"])
def get_notifications(user_id: str) -> tuple[Response, int]:
    """Retrieve all notifications for a user (REQ-012)."""
    notifications = notification_store.get_by_user(user_id)
    return jsonify([n.to_dict() for n in notifications]), 200
