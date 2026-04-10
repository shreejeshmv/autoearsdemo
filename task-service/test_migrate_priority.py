"""Tests for the priority backfill migration (REQ-008)."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import store
from migrate_priority import backfill_priority
from priority import DEFAULT_PRIORITY


class TestBackfillMigration:
    """Tests for the one-time priority backfill migration."""

    def setup_method(self) -> None:
        store.clear_all()

    def test_backfill_tasks_without_priority(self) -> None:
        """REQ-008: tasks without priority get set to medium."""
        store.seed_task({"id": "1", "title": "Legacy 1"})
        store.seed_task({"id": "2", "title": "Legacy 2", "priority": None})
        store.seed_task({"id": "3", "title": "Legacy 3", "priority": ""})
        count = backfill_priority()
        assert count == 3
        for task_id in ("1", "2", "3"):
            assert store.get_task(task_id)["priority"] == DEFAULT_PRIORITY

    def test_backfill_skips_tasks_with_priority(self) -> None:
        store.seed_task({"id": "1", "title": "Has priority", "priority": "high"})
        count = backfill_priority()
        assert count == 0
        assert store.get_task("1")["priority"] == "high"

    def test_backfill_mixed(self) -> None:
        store.seed_task({"id": "1", "title": "No priority"})
        store.seed_task({"id": "2", "title": "Has priority", "priority": "low"})
        count = backfill_priority()
        assert count == 1
        assert store.get_task("1")["priority"] == DEFAULT_PRIORITY
        assert store.get_task("2")["priority"] == "low"

    def test_backfill_empty_store(self) -> None:
        count = backfill_priority()
        assert count == 0

    def test_backfill_idempotent(self) -> None:
        """Running migration twice should not re-count already-backfilled tasks."""
        store.seed_task({"id": "1", "title": "Legacy"})
        first = backfill_priority()
        assert first == 1
        second = backfill_priority()
        assert second == 0
