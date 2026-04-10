"""Tests for the task store."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import store
from priority import DEFAULT_PRIORITY


class TestStore:
    """Tests for store CRUD operations."""

    def setup_method(self) -> None:
        store.clear_all()

    # --- create ---

    def test_create_task_with_default_priority(self) -> None:
        """REQ-002: default to medium when priority not specified."""
        task = store.create_task(title="Test")
        assert task["priority"] == "medium"
        assert task["title"] == "Test"
        assert task["status"] == "open"

    def test_create_task_with_explicit_priority(self) -> None:
        """REQ-001: explicit priority is stored."""
        task = store.create_task(title="Urgent", priority="high")
        assert task["priority"] == "high"

    def test_create_task_has_id(self) -> None:
        task = store.create_task(title="T")
        assert "id" in task and len(task["id"]) > 0

    def test_create_task_with_user_id(self) -> None:
        task = store.create_task(title="T", user_id="u1")
        assert task["user_id"] == "u1"

    # --- read ---

    def test_get_task_found(self) -> None:
        task = store.create_task(title="X")
        fetched = store.get_task(task["id"])
        assert fetched == task

    def test_get_task_not_found(self) -> None:
        assert store.get_task("nonexistent") is None

    # --- list ---

    def test_get_all_tasks_empty(self) -> None:
        assert store.get_all_tasks() == []

    def test_get_all_tasks_returns_all(self) -> None:
        store.create_task(title="A")
        store.create_task(title="B")
        assert len(store.get_all_tasks()) == 2

    def test_get_all_tasks_filter_by_priority(self) -> None:
        """REQ-005: filter by single priority value."""
        store.create_task(title="A", priority="low")
        store.create_task(title="B", priority="high")
        store.create_task(title="C", priority="low")
        low_tasks = store.get_all_tasks(priority_filter="low")
        assert len(low_tasks) == 2
        assert all(t["priority"] == "low" for t in low_tasks)

    def test_get_all_tasks_filter_no_match(self) -> None:
        store.create_task(title="A", priority="low")
        assert store.get_all_tasks(priority_filter="high") == []

    # --- update ---

    def test_update_task_priority(self) -> None:
        """REQ-009: priority is updatable."""
        task = store.create_task(title="T", priority="low")
        updated = store.update_task(task["id"], {"priority": "high"})
        assert updated is not None
        assert updated["priority"] == "high"

    def test_update_task_not_found(self) -> None:
        assert store.update_task("bad", {"title": "X"}) is None

    def test_update_task_ignores_unknown_fields(self) -> None:
        task = store.create_task(title="T")
        updated = store.update_task(task["id"], {"unknown_field": "val"})
        assert updated is not None
        assert "unknown_field" not in updated

    # --- delete ---

    def test_delete_task_found(self) -> None:
        task = store.create_task(title="T")
        assert store.delete_task(task["id"]) is True
        assert store.get_task(task["id"]) is None

    def test_delete_task_not_found(self) -> None:
        assert store.delete_task("bad") is False

    # --- seed ---

    def test_seed_task(self) -> None:
        store.seed_task({"id": "s1", "title": "Seeded", "priority": "low"})
        assert store.get_task("s1")["title"] == "Seeded"
