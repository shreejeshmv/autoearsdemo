"""Task Service – models, helpers, and Flask application."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from flask import Flask, Response, jsonify, request

# ---------------------------------------------------------------------------
# Database layer (in-memory dict; can be swapped for SQLite / Postgres)
# ---------------------------------------------------------------------------

_tasks: Dict[str, Dict[str, Any]] = {}


def _utc_now() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _today_utc() -> date:
    """Return today's date in UTC."""
    return datetime.now(timezone.utc).date()


def _parse_due_date(value: Any) -> Optional[date]:
    """Parse and validate a due_date value.

    Args:
        value: The raw value from the request payload.

    Returns:
        A ``date`` object, or ``None`` if *value* is ``None``.

    Raises:
        ValueError: If *value* is not a valid ``YYYY-MM-DD`` string.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("due_date must be a string in YYYY-MM-DD format.")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid due_date '{value}'. Expected format: YYYY-MM-DD."
        )
    return parsed


def _is_overdue(task: Dict[str, Any]) -> bool:
    """Compute whether a task is overdue.

    A task is overdue when:
    - It has a non-null ``due_date``,
    - The ``due_date`` is strictly before today in UTC, **and**
    - Its ``status`` is not ``completed``.
    """
    due_date_str: Optional[str] = task.get("due_date")
    if due_date_str is None:
        return False
    due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    if task.get("status") == "completed":
        return False
    return due < _today_utc()


def _task_to_response(task: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an internal task dict to a public response dict."""
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task.get("description"),
        "status": task["status"],
        "due_date": task.get("due_date"),
        "overdue": _is_overdue(task),
        "assignee_id": task.get("assignee_id"),
        "created_at": task["created_at"],
        "updated_at": task["updated_at"],
    }


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

VALID_STATUSES = {"pending", "in_progress", "completed"}


def create_task(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new task and store it."""
    title = data.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        raise ValueError("title is required and must be a non-empty string.")

    status = data.get("status", "pending")
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of {sorted(VALID_STATUSES)}."
        )

    due_date_obj = _parse_due_date(data.get("due_date"))

    now = _utc_now()
    task_id = str(uuid.uuid4())
    task: Dict[str, Any] = {
        "id": task_id,
        "title": title.strip(),
        "description": data.get("description"),
        "status": status,
        "due_date": due_date_obj.isoformat() if due_date_obj else None,
        "assignee_id": data.get("assignee_id"),
        "created_at": now,
        "updated_at": now,
    }
    _tasks[task_id] = task
    return task


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a task by ID."""
    return _tasks.get(task_id)


def list_tasks(
    overdue_only: bool = False,
    assignee_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return all tasks, optionally filtered."""
    tasks = list(_tasks.values())
    if assignee_id is not None:
        tasks = [t for t in tasks if t.get("assignee_id") == assignee_id]
    if overdue_only:
        tasks = [t for t in tasks if _is_overdue(t)]
    return tasks


def update_task(task_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing task. Returns ``None`` if not found."""
    task = _tasks.get(task_id)
    if task is None:
        return None

    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string.")
        task["title"] = title.strip()

    if "description" in data:
        task["description"] = data["description"]

    if "status" in data:
        status = data["status"]
        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of {sorted(VALID_STATUSES)}."
            )
        task["status"] = status

    if "due_date" in data:
        due_date_obj = _parse_due_date(data["due_date"])
        task["due_date"] = due_date_obj.isoformat() if due_date_obj else None

    if "assignee_id" in data:
        task["assignee_id"] = data["assignee_id"]

    task["updated_at"] = _utc_now()
    return task


def delete_task(task_id: str) -> bool:
    """Delete a task. Returns ``True`` if the task existed."""
    return _tasks.pop(task_id, None) is not None


def reset_tasks() -> None:
    """Clear all tasks (used in tests)."""
    _tasks.clear()


# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------


def create_app() -> Flask:
    """Application factory for the Task Service."""
    app = Flask(__name__)

    @app.route("/tasks", methods=["GET"])
    def handle_list_tasks() -> tuple[Response, int]:
        overdue_param = request.args.get("overdue", "").lower()
        overdue_only = overdue_param == "true"
        assignee_id = request.args.get("assignee_id")
        tasks = list_tasks(overdue_only=overdue_only, assignee_id=assignee_id)
        return jsonify([_task_to_response(t) for t in tasks]), 200

    @app.route("/tasks", methods=["POST"])
    def handle_create_task() -> tuple[Response, int]:
        data = request.get_json(silent=True) or {}
        try:
            task = create_task(data)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(_task_to_response(task)), 201

    @app.route("/tasks/<task_id>", methods=["GET"])
    def handle_get_task(task_id: str) -> tuple[Response, int]:
        task = get_task(task_id)
        if task is None:
            return jsonify({"error": "Task not found."}), 404
        return jsonify(_task_to_response(task)), 200

    @app.route("/tasks/<task_id>", methods=["PUT"])
    def handle_update_task(task_id: str) -> tuple[Response, int]:
        data = request.get_json(silent=True) or {}
        try:
            task = update_task(task_id, data)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        if task is None:
            return jsonify({"error": "Task not found."}), 404
        return jsonify(_task_to_response(task)), 200

    @app.route("/tasks/<task_id>", methods=["DELETE"])
    def handle_delete_task(task_id: str) -> tuple[Response, int]:
        if delete_task(task_id):
            return jsonify({"message": "Task deleted."}), 200
        return jsonify({"error": "Task not found."}), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
