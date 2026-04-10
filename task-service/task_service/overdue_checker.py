"""Periodic overdue-task checker that notifies users via the user-service."""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional, Set

from .notification_client import NotificationClient
from .store import TaskStore

logger = logging.getLogger(__name__)


class OverdueChecker:
    """Scans the task store for newly overdue tasks and sends notifications."""

    def __init__(
        self,
        store: TaskStore,
        client: NotificationClient,
    ) -> None:
        self._store = store
        self._client = client
        self._notified_task_ids: Set[str] = set()

    def check(self, today: Optional[date] = None) -> int:
        """Check for overdue tasks and notify assigned users.

        Returns the number of *new* notifications sent.
        """
        overdue_tasks = self._store.get_overdue_tasks(today)
        sent = 0
        for task in overdue_tasks:
            if task.id in self._notified_task_ids:
                continue
            if task.assigned_user_id is None:
                continue
            message = (
                f"Task \"{task.title}\" (id={task.id}) is overdue. "
                f"Due date was {task.due_date}."
            )
            try:
                self._client.send_notification(
                    user_id=task.assigned_user_id,
                    message=message,
                    notification_type="overdue_task",
                )
                self._notified_task_ids.add(task.id)
                sent += 1
            except Exception:
                logger.exception(
                    "Failed to notify user %s about task %s",
                    task.assigned_user_id,
                    task.id,
                )
        return sent
