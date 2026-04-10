"""HTTP client for the user-service notification endpoint."""

from __future__ import annotations

from typing import Any, Dict

import requests

DEFAULT_USER_SERVICE_URL = "http://localhost:5001"


class NotificationClient:
    """Thin wrapper around the user-service ``/notifications`` API."""

    def __init__(self, base_url: str = DEFAULT_USER_SERVICE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    def send_notification(
        self,
        user_id: str,
        message: str,
        notification_type: str = "overdue_task",
    ) -> Dict[str, Any]:
        """POST a notification to the user-service.

        Returns the JSON response body on success, or raises on HTTP errors.
        """
        url = f"{self.base_url}/notifications"
        payload = {
            "user_id": user_id,
            "message": message,
            "notification_type": notification_type,
        }
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
