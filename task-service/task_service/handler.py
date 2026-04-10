"""Flask request handlers for the task-service API."""

from __future__ import annotations

from datetime import date

from flask import Flask, Response, jsonify, request

from .models import Task
from .notification_client import NotificationClient
from .overdue_checker import OverdueChecker
from .store import TaskStore

app = Flask(__name__)
store = TaskStore()
notification_client = NotificationClient()
overdue_checker = OverdueChecker(store, notification_client)


def _parse_date(value: str) -> date:
    """Parse an ISO-8601 date string (YYYY-MM-DD).  Raises ``ValueError``."""
    return date.fromisoformat(value)


# -- Task CRUD ----------------------------------------------------------------


@app.route("/tasks", methods=["POST"])
def create_task() -> tuple[Response, int]:
    """Create a new task.  Accepts JSON with ``title``, optional ``due_date``, etc."""
    data = request.get_json(force=True)

    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    due_date_value = None
    if "due_date" in data and data["due_date"] is not None:
        try:
            due_date_value = _parse_date(data["due_date"])
        except (ValueError, TypeError):
            return jsonify({"error": "due_date must be a valid ISO 8601 date (YYYY-MM-DD)"}), 400

    task = Task(
        title=data["title"],
        description=data.get("description", ""),
        status=data.get("status", "pending"),
        due_date=due_date_value,
        assigned_user_id=data.get("assigned_user_id"),
    )
    store.create(task)
    return jsonify(task.to_dict()), 201


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id: str) -> tuple[Response, int]:
    """Retrieve a single task by id."""
    task = store.get(task_id)
    if task is None:
        return jsonify({"error": "task not found"}), 404
    return jsonify(task.to_dict()), 200


@app.route("/tasks", methods=["GET"])
def list_tasks() -> tuple[Response, int]:
    """List tasks with optional filtering and sorting query parameters."""
    sort_by = request.args.get("sort_by")
    due_before_raw = request.args.get("due_before")
    due_after_raw = request.args.get("due_after")
    overdue_raw = request.args.get("overdue", "").lower()

    due_before = None
    if due_before_raw:
        try:
            due_before = _parse_date(due_before_raw)
        except (ValueError, TypeError):
            return jsonify({"error": "due_before must be a valid ISO 8601 date (YYYY-MM-DD)"}), 400

    due_after = None
    if due_after_raw:
        try:
            due_after = _parse_date(due_after_raw)
        except (ValueError, TypeError):
            return jsonify({"error": "due_after must be a valid ISO 8601 date (YYYY-MM-DD)"}), 400

    overdue = overdue_raw == "true"

    tasks = store.list_tasks(
        sort_by=sort_by,
        due_before=due_before,
        due_after=due_after,
        overdue=overdue,
    )
    return jsonify([t.to_dict() for t in tasks]), 200


@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id: str) -> tuple[Response, int]:
    """Update an existing task."""
    data = request.get_json(force=True)

    if not data:
        return jsonify({"error": "request body is required"}), 400

    kwargs: dict = {}
    for field_name in ("title", "description", "status", "assigned_user_id"):
        if field_name in data:
            kwargs[field_name] = data[field_name]

    if "due_date" in data:
        if data["due_date"] is None:
            kwargs["due_date"] = None
        else:
            try:
                kwargs["due_date"] = _parse_date(data["due_date"])
            except (ValueError, TypeError):
                return jsonify({"error": "due_date must be a valid ISO 8601 date (YYYY-MM-DD)"}), 400

    task = store.update(task_id, **kwargs)
    if task is None:
        return jsonify({"error": "task not found"}), 404

    return jsonify(task.to_dict()), 200


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id: str) -> tuple[Response, int]:
    """Delete a task by id."""
    if store.delete(task_id):
        return jsonify({"deleted": True}), 200
    return jsonify({"error": "task not found"}), 404


# -- Overdue check endpoint ---------------------------------------------------


@app.route("/tasks/check-overdue", methods=["POST"])
def check_overdue() -> tuple[Response, int]:
    """Trigger an overdue check and send notifications for newly overdue tasks."""
    sent = overdue_checker.check()
    return jsonify({"notifications_sent": sent}), 200
