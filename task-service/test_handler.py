"""Tests for task-service handlers."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import store
from handler import (
    handle_create_task,
    handle_delete_task,
    handle_get_task,
    handle_list_tasks,
    handle_update_task,
)


class TestHandleCreateTask:
    """Tests for handle_create_task."""

    def setup_method(self) -> None:
        store.clear_all()

    def test_create_with_defaults(self) -> None:
        """REQ-002, REQ-004: priority defaults to medium and is in response."""
        body, status = handle_create_task({"title": "Buy milk"})
        assert status == 201
        assert body["priority"] == "medium"
        assert body["title"] == "Buy milk"

    def test_create_with_explicit_priority(self) -> None:
        """REQ-001: explicit priority accepted."""
        body, status = handle_create_task({"title": "Fix bug", "priority": "high"})
        assert status == 201
        assert body["priority"] == "high"

    def test_create_missing_title(self) -> None:
        body, status = handle_create_task({})
        assert status == 400
        assert "title" in body["error"].lower()

    def test_create_invalid_priority(self) -> None:
        """REQ-006: invalid priority returns 400."""
        body, status = handle_create_task({"title": "T", "priority": "urgent"})
        assert status == 400
        assert "Invalid priority" in body["error"]

    def test_create_with_user_id(self) -> None:
        body, status = handle_create_task({"title": "T", "user_id": "u1"})
        assert status == 201
        assert body["user_id"] == "u1"


class TestHandleListTasks:
    """Tests for handle_list_tasks."""

    def setup_method(self) -> None:
        store.clear_all()

    def test_list_empty(self) -> None:
        body, status = handle_list_tasks({})
        assert status == 200
        assert body == []

    def test_list_all(self) -> None:
        """REQ-004: priority in list response."""
        handle_create_task({"title": "A", "priority": "low"})
        handle_create_task({"title": "B", "priority": "high"})
        body, status = handle_list_tasks({})
        assert status == 200
        assert len(body) == 2
        assert all("priority" in t for t in body)

    def test_list_filter_by_priority(self) -> None:
        """REQ-005: filter by priority query parameter."""
        handle_create_task({"title": "A", "priority": "low"})
        handle_create_task({"title": "B", "priority": "high"})
        handle_create_task({"title": "C", "priority": "low"})
        body, status = handle_list_tasks({"priority": "low"})
        assert status == 200
        assert len(body) == 2

    def test_list_filter_invalid_priority(self) -> None:
        """REQ-007: invalid filter returns 400."""
        body, status = handle_list_tasks({"priority": "critical"})
        assert status == 400
        assert "Invalid priority filter" in body["error"]

    def test_list_filter_no_results(self) -> None:
        handle_create_task({"title": "A", "priority": "low"})
        body, status = handle_list_tasks({"priority": "high"})
        assert status == 200
        assert body == []


class TestHandleGetTask:
    """Tests for handle_get_task."""

    def setup_method(self) -> None:
        store.clear_all()

    def test_get_existing_task(self) -> None:
        """REQ-004: priority in single-task response."""
        created, _ = handle_create_task({"title": "T", "priority": "high"})
        body, status = handle_get_task(created["id"])
        assert status == 200
        assert body["priority"] == "high"

    def test_get_nonexistent_task(self) -> None:
        body, status = handle_get_task("does-not-exist")
        assert status == 404


class TestHandleUpdateTask:
    """Tests for handle_update_task."""

    def setup_method(self) -> None:
        store.clear_all()

    def test_update_priority(self) -> None:
        """REQ-009: priority updatable."""
        created, _ = handle_create_task({"title": "T"})
        body, status = handle_update_task(created["id"], {"priority": "high"})
        assert status == 200
        assert body["priority"] == "high"

    def test_update_invalid_priority(self) -> None:
        """REQ-006: invalid priority on update returns 400."""
        created, _ = handle_create_task({"title": "T"})
        body, status = handle_update_task(created["id"], {"priority": "urgent"})
        assert status == 400
        assert "Invalid priority" in body["error"]

    def test_update_nonexistent_task(self) -> None:
        body, status = handle_update_task("bad", {"title": "X"})
        assert status == 404

    def test_update_title_only(self) -> None:
        created, _ = handle_create_task({"title": "Old"})
        body, status = handle_update_task(created["id"], {"title": "New"})
        assert status == 200
        assert body["title"] == "New"
        assert body["priority"] == "medium"  # unchanged


class TestHandleDeleteTask:
    """Tests for handle_delete_task."""

    def setup_method(self) -> None:
        store.clear_all()

    def test_delete_existing(self) -> None:
        created, _ = handle_create_task({"title": "T"})
        body, status = handle_delete_task(created["id"])
        assert status == 200

    def test_delete_nonexistent(self) -> None:
        body, status = handle_delete_task("bad")
        assert status == 404
