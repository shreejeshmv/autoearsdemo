"""Task data models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Task:
    """Represents a task with an optional due date."""

    title: str
    description: str = ""
    status: str = "pending"
    due_date: Optional[date] = None
    assigned_user_id: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def is_overdue(self, today: Optional[date] = None) -> bool:
        """Check whether the task is overdue.

        A task is overdue when it has a due_date earlier than *today* and
        its status is not ``"completed"``.
        """
        if self.due_date is None:
            return False
        reference = today if today is not None else date.today()
        return self.due_date < reference and self.status != "completed"

    def to_dict(self, today: Optional[date] = None) -> dict:
        """Serialise the task to a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "assigned_user_id": self.assigned_user_id,
            "is_overdue": self.is_overdue(today),
        }
