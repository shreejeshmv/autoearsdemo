"""Tests for task-service models."""

from datetime import date

from task_service.models import Task


class TestTaskModel:
    """Tests for the Task dataclass."""

    def test_create_task_without_due_date(self) -> None:
        task = Task(title="Buy groceries")
        assert task.title == "Buy groceries"
        assert task.due_date is None
        assert task.status == "pending"
        assert task.is_overdue() is False

    def test_create_task_with_due_date(self) -> None:
        task = Task(title="File taxes", due_date=date(2025, 4, 15))
        assert task.due_date == date(2025, 4, 15)

    def test_is_overdue_when_past_due_and_pending(self) -> None:
        task = Task(title="Old task", due_date=date(2020, 1, 1), status="pending")
        assert task.is_overdue(today=date(2025, 6, 1)) is True

    def test_is_not_overdue_when_completed(self) -> None:
        task = Task(title="Done task", due_date=date(2020, 1, 1), status="completed")
        assert task.is_overdue(today=date(2025, 6, 1)) is False

    def test_is_not_overdue_when_due_today(self) -> None:
        today = date(2025, 6, 1)
        task = Task(title="Today task", due_date=today, status="pending")
        assert task.is_overdue(today=today) is False

    def test_is_not_overdue_when_due_in_future(self) -> None:
        task = Task(title="Future task", due_date=date(2099, 12, 31), status="pending")
        assert task.is_overdue(today=date(2025, 6, 1)) is False

    def test_is_not_overdue_when_no_due_date(self) -> None:
        task = Task(title="No date", due_date=None)
        assert task.is_overdue() is False

    def test_to_dict_includes_due_date_and_overdue_flag(self) -> None:
        task = Task(title="Test", due_date=date(2020, 1, 1), status="pending", assigned_user_id="u1")
        d = task.to_dict(today=date(2025, 6, 1))
        assert d["due_date"] == "2020-01-01"
        assert d["is_overdue"] is True
        assert d["assigned_user_id"] == "u1"

    def test_to_dict_null_due_date(self) -> None:
        task = Task(title="Test")
        d = task.to_dict()
        assert d["due_date"] is None
        assert d["is_overdue"] is False
