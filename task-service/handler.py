"""Request handlers (route logic) for the task-service."""

from typing import Any, Dict, Tuple

from priority import validate_priority, VALID_PRIORITIES
import store


def handle_create_task(body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Handle POST /tasks.

    Args:
        body: Parsed JSON request body.

    Returns:
        Tuple of (response_body, status_code).
    """
    title = body.get("title")
    if not title:
        return {"error": "Field 'title' is required."}, 400

    priority = body.get("priority")
    try:
        priority = validate_priority(priority)
    except ValueError as exc:
        return {"error": str(exc)}, 400

    task = store.create_task(
        title=title,
        description=body.get("description", ""),
        priority=priority,
        user_id=body.get("user_id"),
    )
    return task, 201


def handle_list_tasks(args: Dict[str, str]) -> Tuple[Any, int]:
    """Handle GET /tasks.

    Args:
        args: Query-string parameters.

    Returns:
        Tuple of (response_body, status_code).
    """
    priority_filter = args.get("priority")
    if priority_filter is not None:
        if priority_filter not in VALID_PRIORITIES:
            return {
                "error": (
                    f"Invalid priority filter '{priority_filter}'. "
                    f"Allowed values: {', '.join(sorted(VALID_PRIORITIES))}"
                )
            }, 400

    tasks = store.get_all_tasks(priority_filter=priority_filter)
    return tasks, 200


def handle_get_task(task_id: str) -> Tuple[Dict[str, Any], int]:
    """Handle GET /tasks/<task_id>.

    Returns:
        Tuple of (response_body, status_code).
    """
    task = store.get_task(task_id)
    if task is None:
        return {"error": "Task not found."}, 404
    return task, 200


def handle_update_task(
    task_id: str, body: Dict[str, Any]
) -> Tuple[Dict[str, Any], int]:
    """Handle PUT /tasks/<task_id>.

    Args:
        task_id: The task ID from the URL path.
        body: Parsed JSON request body.

    Returns:
        Tuple of (response_body, status_code).
    """
    priority = body.get("priority")
    try:
        priority = validate_priority(priority)
    except ValueError as exc:
        return {"error": str(exc)}, 400

    # Build updates dict — only include fields that were provided
    updates: Dict[str, Any] = {}
    for field in ("title", "description", "status", "user_id"):
        if field in body:
            updates[field] = body[field]
    if priority is not None:
        updates["priority"] = priority

    task = store.update_task(task_id, updates)
    if task is None:
        return {"error": "Task not found."}, 404
    return task, 200


def handle_delete_task(task_id: str) -> Tuple[Dict[str, Any], int]:
    """Handle DELETE /tasks/<task_id>.

    Returns:
        Tuple of (response_body, status_code).
    """
    deleted = store.delete_task(task_id)
    if not deleted:
        return {"error": "Task not found."}, 404
    return {"message": "Task deleted."}, 200
