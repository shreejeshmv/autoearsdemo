"""In-memory stores for users and notifications."""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import Notification, User


class UserStore:
    """Simple in-memory store for users."""

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def create(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def get(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def list_users(self) -> List[User]:
        return list(self._users.values())


class NotificationStore:
    """Simple in-memory store for notifications."""

    def __init__(self) -> None:
        self._notifications: Dict[str, Notification] = {}

    def create(self, notification: Notification) -> Notification:
        self._notifications[notification.id] = notification
        return notification

    def get_by_user(self, user_id: str) -> List[Notification]:
        """Return all notifications for a given user, newest first."""
        return sorted(
            [n for n in self._notifications.values() if n.user_id == user_id],
            key=lambda n: n.created_at,
            reverse=True,
        )
