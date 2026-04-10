"""In-memory task store with filtering, sorting, and CRUD operations."""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from .models import Task


class TaskStore:
    """Simple in-memory store for tasks."""

    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}

    # -- CRUD -----------------------------------------------------------------

    def create(self, task: Task) -> Task:
        """Persist a new task and return it."""
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Return a single task by id, or ``None``."""
        return self._tasks.get(task_id)

    def update(self, task_id: str, **kwargs: object) -> Optional[Task]:
        """Update fields on an existing task.  Returns the updated task or ``None``."""
        task = self._tasks.get(task_id)
        if task is None:
            return None
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        return task

    def delete(self, task_id: str) -> bool:
        """Delete a task.  Returns ``True`` if deleted."""
        return self._tasks.pop(task_id, None) is not None

    # -- Query / List ---------------------------------------------------------

    def list_tasks(
        self,
        *,
        sort_by: Optional[str] = None,
        due_before: Optional[date] = None,
        due_after: Optional[date] = None,
        overdue: bool = False,
        today: Optional[date] = None,
    ) -> List[Task]:
        """Return tasks with optional filtering and sorting.

        Parameters
        ----------
        sort_by:
            If ``"due_date"``, sort ascending with ``None`` due-dates last.
        due_before:
            Only include tasks whose ``due_date <= due_before``.
        due_after:
            Only include tasks whose ``due_date >= due_after``.
        overdue:
            If ``True``, only include overdue tasks.
        today:
            Reference date for the overdue check (defaults to ``date.today()``).
        """
        reference = today if today is not None else date.today()
        tasks = list(self._tasks.values())

        # -- Filtering --------------------------------------------------------
        if due_before is not None:
            tasks = [t for t in tasks if t.due_date is not None and t.due_date <= due_before]

        if due_after is not None:
            tasks = [t for t in tasks if t.due_date is not None and t.due_date >= due_after]

        if overdue:
            tasks = [t for t in tasks if t.is_overdue(reference)]

        # -- Sorting ----------------------------------------------------------
        if sort_by == "due_date":
            tasks.sort(key=lambda t: (t.due_date is None, t.due_date or date.max))

        return tasks

    # -- Overdue helpers ------------------------------------------------------

    def get_overdue_tasks(self, today: Optional[date] = None) -> List[Task]:
        """Return all tasks that are currently overdue."""
        reference = today if today is not None else date.today()
        return [t for t in self._tasks.values() if t.is_overdue(reference)]
