"""Comprehensive tests for the Task Service, focusing on due-date functionality."""

from __future__ import annotations

import json
from datetime import date, timedelta, datetime, timezone
from typing import Any, Dict
from unittest.mock import patch

import pytest

from app import create_app, reset_tasks, _tasks


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    """Create a test client and reset state between tests."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        reset_tasks()
        yield c
        reset_tasks()


def _post_task(client, payload: Dict[str, Any] | None = None):
    """Helper – POST a task and return the response."""
    if payload is None:
        payload = {"title": "Test task"}
    return client.post(
        "/tasks",
        data=json.dumps(payload),
        content_type="application/json",
    )


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------


class TestCreateTask:
    def test_create_minimal(self, client):
        resp = _post_task(client, {"title": "Buy milk"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "Buy milk"
        assert data["status"] == "pending"
        assert data["due_date"] is None
        assert data["overdue"] is False

    def test_create_with_due_date(self, client):
        resp = _post_task(client, {"title": "Pay bills", "due_date": "2099-12-31"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["due_date"] == "2099-12-31"
        assert data["overdue"] is False

    def test_create_missing_title(self, client):
        resp = _post_task(client, {"description": "no title"})
        assert resp.status_code == 400

    def test_create_invalid_status(self, client):
        resp = _post_task(client, {"title": "T", "status": "unknown"})
        assert resp.status_code == 400

    def test_create_with_assignee(self, client):
        resp = _post_task(
            client,
            {"title": "Assigned task", "assignee_id": "user-1"},
        )
        assert resp.status_code == 201
        assert resp.get_json()["assignee_id"] == "user-1"


class TestGetTask:
    def test_get_existing(self, client):
        task_id = _post_task(client).get_json()["id"]
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == task_id

    def test_get_not_found(self, client):
        resp = client.get("/tasks/nonexistent")
        assert resp.status_code == 404


class TestListTasks:
    def test_list_empty(self, client):
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_multiple(self, client):
        _post_task(client, {"title": "A"})
        _post_task(client, {"title": "B"})
        resp = client.get("/tasks")
        assert len(resp.get_json()) == 2

    def test_list_filter_assignee(self, client):
        _post_task(client, {"title": "A", "assignee_id": "u1"})
        _post_task(client, {"title": "B", "assignee_id": "u2"})
        resp = client.get("/tasks?assignee_id=u1")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["assignee_id"] == "u1"


class TestUpdateTask:
    def test_update_title(self, client):
        task_id = _post_task(client).get_json()["id"]
        resp = client.put(
            f"/tasks/{task_id}",
            data=json.dumps({"title": "Updated"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["title"] == "Updated"

    def test_update_not_found(self, client):
        resp = client.put(
            "/tasks/nonexistent",
            data=json.dumps({"title": "X"}),
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_update_invalid_status(self, client):
        task_id = _post_task(client).get_json()["id"]
        resp = client.put(
            f"/tasks/{task_id}",
            data=json.dumps({"status": "bad"}),
            content_type="application/json",
        )
        assert resp.status_code == 400


class TestDeleteTask:
    def test_delete_existing(self, client):
        task_id = _post_task(client).get_json()["id"]
        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 200
        assert client.get(f"/tasks/{task_id}").status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/tasks/nonexistent")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Due-date specific (REQ-001 through REQ-010)
# ---------------------------------------------------------------------------


class TestDueDateValidation:
    """REQ-008: Invalid due_date → 400."""

    def test_invalid_format_slash(self, client):
        resp = _post_task(client, {"title": "T", "due_date": "12/31/2025"})
        assert resp.status_code == 400
        assert "due_date" in resp.get_json()["error"].lower()

    def test_invalid_format_word(self, client):
        resp = _post_task(client, {"title": "T", "due_date": "tomorrow"})
        assert resp.status_code == 400

    def test_invalid_format_number(self, client):
        resp = _post_task(client, {"title": "T", "due_date": 12345})
        assert resp.status_code == 400

    def test_invalid_format_partial(self, client):
        resp = _post_task(client, {"title": "T", "due_date": "2025-13-01"})
        assert resp.status_code == 400

    def test_null_due_date_accepted(self, client):
        resp = _post_task(client, {"title": "T", "due_date": None})
        assert resp.status_code == 201
        assert resp.get_json()["due_date"] is None

    def test_valid_due_date_accepted(self, client):
        resp = _post_task(client, {"title": "T", "due_date": "2025-06-15"})
        assert resp.status_code == 201
        assert resp.get_json()["due_date"] == "2025-06-15"

    def test_update_invalid_due_date(self, client):
        task_id = _post_task(client).get_json()["id"]
        resp = client.put(
            f"/tasks/{task_id}",
            data=json.dumps({"due_date": "not-a-date"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_update_valid_due_date(self, client):
        task_id = _post_task(client).get_json()["id"]
        resp = client.put(
            f"/tasks/{task_id}",
            data=json.dumps({"due_date": "2030-01-01"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["due_date"] == "2030-01-01"

    def test_update_clear_due_date(self, client):
        task_id = _post_task(
            client, {"title": "T", "due_date": "2030-01-01"}
        ).get_json()["id"]
        resp = client.put(
            f"/tasks/{task_id}",
            data=json.dumps({"due_date": None}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["due_date"] is None


class TestOverdueFlag:
    """REQ-005, REQ-006: overdue flag computation."""

    def test_no_due_date_not_overdue(self, client):
        """REQ-006: No due_date → overdue is False."""
        resp = _post_task(client, {"title": "T"})
        assert resp.get_json()["overdue"] is False

    def test_future_due_date_not_overdue(self, client):
        future = (date.today() + timedelta(days=30)).isoformat()
        resp = _post_task(client, {"title": "T", "due_date": future})
        assert resp.get_json()["overdue"] is False

    def test_today_due_date_not_overdue(self, client):
        """Task due today is NOT overdue (overdue means due_date < today)."""
        today = date.today().isoformat()
        resp = _post_task(client, {"title": "T", "due_date": today})
        assert resp.get_json()["overdue"] is False

    def test_past_due_date_is_overdue(self, client):
        past = (date.today() - timedelta(days=1)).isoformat()
        resp = _post_task(client, {"title": "T", "due_date": past})
        assert resp.get_json()["overdue"] is True

    def test_past_due_date_completed_not_overdue(self, client):
        """REQ-005: Completed tasks are not overdue."""
        past = (date.today() - timedelta(days=1)).isoformat()
        resp = _post_task(
            client,
            {"title": "T", "due_date": past, "status": "completed"},
        )
        assert resp.get_json()["overdue"] is False

    def test_overdue_flag_on_get(self, client):
        past = (date.today() - timedelta(days=5)).isoformat()
        task_id = _post_task(
            client, {"title": "T", "due_date": past}
        ).get_json()["id"]
        resp = client.get(f"/tasks/{task_id}")
        assert resp.get_json()["overdue"] is True

    def test_overdue_flag_in_list(self, client):
        past = (date.today() - timedelta(days=5)).isoformat()
        _post_task(client, {"title": "T", "due_date": past})
        resp = client.get("/tasks")
        assert resp.get_json()[0]["overdue"] is True

    def test_marking_completed_clears_overdue(self, client):
        """Updating status to completed should make overdue False."""
        past = (date.today() - timedelta(days=1)).isoformat()
        task_id = _post_task(
            client, {"title": "T", "due_date": past}
        ).get_json()["id"]
        # Confirm overdue
        assert client.get(f"/tasks/{task_id}").get_json()["overdue"] is True
        # Mark completed
        resp = client.put(
            f"/tasks/{task_id}",
            data=json.dumps({"status": "completed"}),
            content_type="application/json",
        )
        assert resp.get_json()["overdue"] is False


class TestOverdueFilter:
    """REQ-010: ?overdue=true filter."""

    def test_overdue_filter(self, client):
        past = (date.today() - timedelta(days=2)).isoformat()
        future = (date.today() + timedelta(days=30)).isoformat()
        _post_task(client, {"title": "Overdue", "due_date": past})
        _post_task(client, {"title": "Future", "due_date": future})
        _post_task(client, {"title": "No date"})

        resp = client.get("/tasks?overdue=true")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Overdue"

    def test_overdue_filter_excludes_completed(self, client):
        past = (date.today() - timedelta(days=2)).isoformat()
        _post_task(
            client,
            {"title": "Done", "due_date": past, "status": "completed"},
        )
        resp = client.get("/tasks?overdue=true")
        assert resp.get_json() == []

    def test_no_overdue_filter_returns_all(self, client):
        past = (date.today() - timedelta(days=2)).isoformat()
        _post_task(client, {"title": "A", "due_date": past})
        _post_task(client, {"title": "B"})
        resp = client.get("/tasks")
        assert len(resp.get_json()) == 2

    def test_overdue_filter_false_returns_all(self, client):
        """?overdue=false should behave like no filter."""
        past = (date.today() - timedelta(days=2)).isoformat()
        _post_task(client, {"title": "A", "due_date": past})
        _post_task(client, {"title": "B"})
        resp = client.get("/tasks?overdue=false")
        assert len(resp.get_json()) == 2


class TestResponsePayload:
    """REQ-004: due_date and overdue present in all responses."""

    def test_create_response_has_fields(self, client):
        resp = _post_task(client, {"title": "T"})
        data = resp.get_json()
        assert "due_date" in data
        assert "overdue" in data

    def test_get_response_has_fields(self, client):
        task_id = _post_task(client).get_json()["id"]
        data = client.get(f"/tasks/{task_id}").get_json()
        assert "due_date" in data
        assert "overdue" in data

    def test_list_response_has_fields(self, client):
        _post_task(client)
        data = client.get("/tasks").get_json()
        assert "due_date" in data[0]
        assert "overdue" in data[0]

    def test_update_response_has_fields(self, client):
        task_id = _post_task(client).get_json()["id"]
        resp = client.put(
            f"/tasks/{task_id}",
            data=json.dumps({"title": "U"}),
            content_type="application/json",
        )
        data = resp.get_json()
        assert "due_date" in data
        assert "overdue" in data


class TestLegacyTaskCompat:
    """REQ-009: Tasks without due_date default to null."""

    def test_legacy_task_defaults(self, client):
        """Simulate a legacy task by inserting directly into the store."""
        from app import _tasks, _utc_now

        now = _utc_now()
        _tasks["legacy-1"] = {
            "id": "legacy-1",
            "title": "Old task",
            "description": None,
            "status": "pending",
            "assignee_id": None,
            "created_at": now,
            "updated_at": now,
            # no due_date key at all
        }
        resp = client.get("/tasks/legacy-1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["due_date"] is None
        assert data["overdue"] is False
