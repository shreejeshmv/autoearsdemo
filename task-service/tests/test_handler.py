"""Tests for task-service Flask API handlers."""

import json
from datetime import date

import pytest

from task_service.handler import app, store


@pytest.fixture(autouse=True)
def _clear_store() -> None:
    """Reset the in-memory store between tests."""
    store._tasks.clear()


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestCreateTask:
    def test_create_with_due_date(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T1", "due_date": "2025-07-01"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["due_date"] == "2025-07-01"
        assert data["is_overdue"] is False

    def test_create_without_due_date(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T2"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["due_date"] is None
        assert data["is_overdue"] is False

    def test_create_with_null_due_date(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T3", "due_date": None})
        assert resp.status_code == 201
        assert resp.get_json()["due_date"] is None

    def test_create_with_invalid_due_date(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T4", "due_date": "not-a-date"})
        assert resp.status_code == 400
        assert "due_date" in resp.get_json()["error"]

    def test_create_missing_title(self, client) -> None:
        resp = client.post("/tasks", json={"due_date": "2025-01-01"})
        assert resp.status_code == 400


class TestGetTask:
    def test_get_existing(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T1", "due_date": "2025-07-01"})
        task_id = resp.get_json()["id"]
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.get_json()["title"] == "T1"

    def test_get_missing(self, client) -> None:
        resp = client.get("/tasks/nonexistent")
        assert resp.status_code == 404


class TestUpdateTask:
    def test_update_due_date(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T1"})
        task_id = resp.get_json()["id"]
        resp = client.put(f"/tasks/{task_id}", json={"due_date": "2025-08-15"})
        assert resp.status_code == 200
        assert resp.get_json()["due_date"] == "2025-08-15"

    def test_clear_due_date(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T1", "due_date": "2025-08-15"})
        task_id = resp.get_json()["id"]
        resp = client.put(f"/tasks/{task_id}", json={"due_date": None})
        assert resp.status_code == 200
        assert resp.get_json()["due_date"] is None

    def test_update_invalid_due_date(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T1"})
        task_id = resp.get_json()["id"]
        resp = client.put(f"/tasks/{task_id}", json={"due_date": "bad"})
        assert resp.status_code == 400

    def test_update_missing_task(self, client) -> None:
        resp = client.put("/tasks/missing", json={"title": "X"})
        assert resp.status_code == 404


class TestDeleteTask:
    def test_delete_existing(self, client) -> None:
        resp = client.post("/tasks", json={"title": "T1"})
        task_id = resp.get_json()["id"]
        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 200

    def test_delete_missing(self, client) -> None:
        resp = client.delete("/tasks/missing")
        assert resp.status_code == 404


class TestListTasks:
    def test_list_all(self, client) -> None:
        client.post("/tasks", json={"title": "A"})
        client.post("/tasks", json={"title": "B"})
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_sort_by_due_date(self, client) -> None:
        client.post("/tasks", json={"title": "No date"})
        client.post("/tasks", json={"title": "Later", "due_date": "2025-12-01"})
        client.post("/tasks", json={"title": "Earlier", "due_date": "2025-01-01"})
        resp = client.get("/tasks?sort_by=due_date")
        titles = [t["title"] for t in resp.get_json()]
        assert titles == ["Earlier", "Later", "No date"]

    def test_filter_due_before(self, client) -> None:
        client.post("/tasks", json={"title": "A", "due_date": "2025-01-01"})
        client.post("/tasks", json={"title": "B", "due_date": "2025-06-01"})
        client.post("/tasks", json={"title": "C", "due_date": "2025-12-01"})
        resp = client.get("/tasks?due_before=2025-06-01")
        titles = {t["title"] for t in resp.get_json()}
        assert titles == {"A", "B"}

    def test_filter_due_after(self, client) -> None:
        client.post("/tasks", json={"title": "A", "due_date": "2025-01-01"})
        client.post("/tasks", json={"title": "B", "due_date": "2025-06-01"})
        client.post("/tasks", json={"title": "C", "due_date": "2025-12-01"})
        resp = client.get("/tasks?due_after=2025-06-01")
        titles = {t["title"] for t in resp.get_json()}
        assert titles == {"B", "C"}

    def test_filter_overdue(self, client) -> None:
        client.post("/tasks", json={"title": "Old", "due_date": "2020-01-01"})
        client.post("/tasks", json={"title": "Future", "due_date": "2099-01-01"})
        resp = client.get("/tasks?overdue=true")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Old"

    def test_filter_due_before_invalid(self, client) -> None:
        resp = client.get("/tasks?due_before=nope")
        assert resp.status_code == 400

    def test_filter_due_after_invalid(self, client) -> None:
        resp = client.get("/tasks?due_after=nope")
        assert resp.status_code == 400


class TestOverdueFlag:
    def test_overdue_flag_in_response(self, client) -> None:
        resp = client.post(
            "/tasks",
            json={"title": "Old task", "due_date": "2020-01-01", "status": "pending"},
        )
        data = resp.get_json()
        assert data["is_overdue"] is True

    def test_completed_task_not_overdue(self, client) -> None:
        resp = client.post(
            "/tasks",
            json={"title": "Done task", "due_date": "2020-01-01", "status": "completed"},
        )
        data = resp.get_json()
        assert data["is_overdue"] is False
