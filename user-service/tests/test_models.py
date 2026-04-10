"""Tests for user-service models."""

from user_service.models import Notification, User


class TestUserModel:
    def test_create_user(self) -> None:
        user = User(name="Alice", email="alice@example.com")
        assert user.name == "Alice"
        assert user.email == "alice@example.com"
        assert user.id  # non-empty

    def test_user_default_email(self) -> None:
        user = User(name="Bob")
        assert user.email == ""


class TestNotificationModel:
    def test_create_notification(self) -> None:
        n = Notification(user_id="u1", message="Hello", notification_type="overdue_task")
        assert n.user_id == "u1"
        assert n.message == "Hello"
        assert n.notification_type == "overdue_task"
        assert n.id  # non-empty
        assert n.created_at  # non-empty

    def test_to_dict(self) -> None:
        n = Notification(user_id="u1", message="Hi")
        d = n.to_dict()
        assert d["user_id"] == "u1"
        assert d["message"] == "Hi"
        assert "id" in d
        assert "created_at" in d
        assert "notification_type" in d
