"""Tests for the User Service."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any, Dict, List
from unittest.mock import patch, MagicMock

import pytest

from app import create_app, reset_users


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        reset_users()
        yield c
        reset_users()


def _post_user(client, payload: Dict[str, Any] | None = None):
    if payload is None:
        payload = {"name": "Alice", "email": "alice@example.com"}
    return client.post(
        "/users",
        data=json.dumps(payload),
        content_type="application/json",
    )


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------


class TestCreateUser:
    def test_create_minimal(self, client):
        resp = _post_user(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Alice"
        assert data["email"] == "alice@example.com"
        assert "id" in data
        assert "created_at" in data

    def test_create_missing_name(self, client):
        resp = _post_user(client, {"email": "a@b.com"})
        assert resp.status_code == 400

    def test_create_missing_email(self, client):
        resp = _post_user(client, {"name": "Bob"})
        assert resp.status_code == 400


class TestGetUser:
    def test_get_existing(self, client):
        user_id = _post_user(client).get_json()["id"]
        resp = client.get(f"/users/{user_id}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == user_id

    def test_get_not_found(self, client):
        resp = client.get("/users/nonexistent")
        assert resp.status_code == 404


class TestListUsers:
    def test_list_empty(self, client):
        resp = client.get("/users")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_multiple(self, client):
        _post_user(client, {"name": "A", "email": "a@b.com"})
        _post_user(client, {"name": "B", "email": "b@b.com"})
        resp = client.get("/users")
        assert len(resp.get_json()) == 2


class TestUpdateUser:
    def test_update_name(self, client):
        user_id = _post_user(client).get_json()["id"]
        resp = client.put(
            f"/users/{user_id}",
            data=json.dumps({"name": "Bob"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Bob"

    def test_update_not_found(self, client):
        resp = client.put(
            "/users/nonexistent",
            data=json.dumps({"name": "X"}),
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_update_invalid_name(self, client):
        user_id = _post_user(client).get_json()["id"]
        resp = client.put(
            f"/users/{user_id}",
            data=json.dumps({"name": ""}),
            content_type="application/json",
        )
        assert resp.status_code == 400


class TestDeleteUser:
    def test_delete_existing(self, client):
        user_id = _post_user(client).get_json()["id"]
        resp = client.delete(f"/users/{user_id}")
        assert resp.status_code == 200
        assert client.get(f"/users/{user_id}").status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/users/nonexistent")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# User-Tasks proxy endpoint (calls task-service)
# ---------------------------------------------------------------------------


class TestUserTasks:
    """Test GET /users/<id>/tasks which proxies to the task service."""

    def test_user_not_found(self, client):
        resp = client.get("/users/nonexistent/tasks")
        assert resp.status_code == 404

    @patch("app.fetch_user_tasks")
    def test_user_tasks_success(self, mock_fetch, client):
        user_id = _post_user(client).get_json()["id"]
        mock_fetch.return_value = [
            {
                "id": "t1",
                "title": "Task 1",
                "status": "pending",
                "due_date": "2025-07-01",
                "overdue": False,
            }
        ]
        resp = client.get(f"/users/{user_id}/tasks")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["due_date"] == "2025-07-01"
        mock_fetch.assert_called_once_with(user_id, overdue_only=False)

    @patch("app.fetch_user_tasks")
    def test_user_tasks_overdue_filter(self, mock_fetch, client):
        user_id = _post_user(client).get_json()["id"]
        past = (date.today() - timedelta(days=3)).isoformat()
        mock_fetch.return_value = [
            {
                "id": "t2",
                "title": "Overdue task",
                "status": "pending",
                "due_date": past,
                "overdue": True,
            }
        ]
        resp = client.get(f"/users/{user_id}/tasks?overdue=true")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["overdue"] is True
        mock_fetch.assert_called_once_with(user_id, overdue_only=True)

    @patch("app.fetch_user_tasks")
    def test_user_tasks_service_down(self, mock_fetch, client):
        import requests as req_lib

        user_id = _post_user(client).get_json()["id"]
        mock_fetch.side_effect = req_lib.ConnectionError("refused")
        resp = client.get(f"/users/{user_id}/tasks")
        assert resp.status_code == 502
