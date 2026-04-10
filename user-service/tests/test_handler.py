"""Tests for user-service Flask API handlers."""

import pytest

from user_service.handler import app, notification_store, user_store


@pytest.fixture(autouse=True)
def _clear_stores() -> None:
    """Reset in-memory stores between tests."""
    user_store._users.clear()
    notification_store._notifications.clear()


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestUserEndpoints:
    def test_create_user(self, client) -> None:
        resp = client.post("/users", json={"name": "Alice", "email": "a@b.com"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Alice"
        assert "id" in data

    def test_create_user_missing_name(self, client) -> None:
        resp = client.post("/users", json={"email": "a@b.com"})
        assert resp.status_code == 400

    def test_get_user(self, client) -> None:
        resp = client.post("/users", json={"name": "Bob"})
        user_id = resp.get_json()["id"]
        resp = client.get(f"/users/{user_id}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Bob"

    def test_get_user_not_found(self, client) -> None:
        resp = client.get("/users/missing")
        assert resp.status_code == 404


class TestNotificationEndpoints:
    def test_create_notification(self, client) -> None:
        resp = client.post(
            "/notifications",
            json={
                "user_id": "u1",
                "message": "Your task is overdue",
                "notification_type": "overdue_task",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["user_id"] == "u1"
        assert data["message"] == "Your task is overdue"
        assert data["notification_type"] == "overdue_task"
        assert "id" in data
        assert "created_at" in data

    def test_create_notification_missing_fields(self, client) -> None:
        resp = client.post("/notifications", json={"user_id": "u1"})
        assert resp.status_code == 400

    def test_create_notification_missing_user_id(self, client) -> None:
        resp = client.post("/notifications", json={"message": "hello"})
        assert resp.status_code == 400

    def test_create_notification_empty_body(self, client) -> None:
        resp = client.post("/notifications", json={})
        assert resp.status_code == 400

    def test_get_notifications_for_user(self, client) -> None:
        client.post(
            "/notifications",
            json={"user_id": "u1", "message": "Msg 1", "notification_type": "overdue_task"},
        )
        client.post(
            "/notifications",
            json={"user_id": "u1", "message": "Msg 2", "notification_type": "overdue_task"},
        )
        client.post(
            "/notifications",
            json={"user_id": "u2", "message": "Other user"},
        )
        resp = client.get("/notifications/u1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        # All notifications belong to u1
        assert all(n["user_id"] == "u1" for n in data)

    def test_get_notifications_empty(self, client) -> None:
        resp = client.get("/notifications/nobody")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_default_notification_type(self, client) -> None:
        resp = client.post(
            "/notifications",
            json={"user_id": "u1", "message": "Test"},
        )
        assert resp.status_code == 201
        assert resp.get_json()["notification_type"] == "overdue_task"

    def test_custom_notification_type(self, client) -> None:
        resp = client.post(
            "/notifications",
            json={
                "user_id": "u1",
                "message": "Reminder",
                "notification_type": "reminder",
            },
        )
        assert resp.status_code == 201
        assert resp.get_json()["notification_type"] == "reminder"

    def test_notification_response_structure(self, client) -> None:
        """Verify the notification response contains all required fields (REQ-013)."""
        resp = client.post(
            "/notifications",
            json={
                "user_id": "u1",
                "message": "Task overdue",
                "notification_type": "overdue_task",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert set(data.keys()) == {
            "id",
            "user_id",
            "message",
            "notification_type",
            "created_at",
        }
