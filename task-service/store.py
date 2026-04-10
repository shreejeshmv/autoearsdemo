"""In-memory data store for tasks."""

from typing import Any, Dict, Optional
import uuid

from priority import DEFAULT_PRIORITY


# In-memory task storage: task_id -> task dict
_tasks: Dict[str, Dict[str, Any]] = {}


def get_all_tasks(priority_filter: Optional[str] = None) -> list[Dict[str, Any]]:
    """Return all tasks, optionally filtered by priority.

    Args:
        priority_filter: If provided, only return tasks with this priority.

    Returns:
        A list of task dictionaries.
    """
    tasks = list(_tasks.values())
    if priority_filter is not None:
        tasks = [t for t in tasks if t.get("priority") == priority_filter]
    return tasks


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Return a single task by ID, or None if not found."""
    return _tasks.get(task_id)


def create_task(
    title: str,
    description: str = "",
    priority: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new task and store it.

    Args:
        title: The task title.
        description: The task description.
        priority: The task priority (defaults to DEFAULT_PRIORITY).
        user_id: Optional ID of the user who owns the task.

    Returns:
        The created task dictionary.
    """
    task_id = str(uuid.uuid4())
    task: Dict[str, Any] = {
        "id": task_id,
        "title": title,
        "description": description,
        "priority": priority if priority is not None else DEFAULT_PRIORITY,
        "status": "open",
        "user_id": user_id,
    }
    _tasks[task_id] = task
    return task


def update_task(task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing task.

    Args:
        task_id: The ID of the task to update.
        updates: A dictionary of fields to update.

    Returns:
        The updated task dictionary, or None if not found.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None
    allowed_fields = {"title", "description", "priority", "status", "user_id"}
    for key, value in updates.items():
        if key in allowed_fields:
            task[key] = value
    return task


def delete_task(task_id: str) -> bool:
    """Delete a task by ID.

    Returns:
        True if the task was deleted, False if not found.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def clear_all() -> None:
    """Remove all tasks (used for testing)."""
    _tasks.clear()


def seed_task(task: Dict[str, Any]) -> None:
    """Insert a task directly (used for testing and migration)."""
    _tasks[task["id"]] = task
