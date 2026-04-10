"""User-service data models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """Represents a user."""

    name: str
    email: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Notification:
    """Represents a notification sent to a user."""

    user_id: str
    message: str
    notification_type: str = "overdue_task"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        """Serialise to a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "notification_type": self.notification_type,
            "created_at": self.created_at,
        }
