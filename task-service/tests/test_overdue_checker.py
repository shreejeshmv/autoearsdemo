"""Tests for task-service overdue checker."""

from datetime import date
from unittest.mock import MagicMock

from task_service.models import Task
from task_service.overdue_checker import OverdueChecker
from task_service.store import TaskStore


class TestOverdueChecker:
    def test_sends_notification_for_overdue_task(self) -> None:
        store = TaskStore()
        store.create(
            Task(
                title="Late",
                due_date=date(2020, 1, 1),
                status="pending",
                assigned_user_id="user-1",
            )
        )
        client = MagicMock()
        client.send_notification.return_value = {"id": "n1"}
        checker = OverdueChecker(store, client)

        sent = checker.check(today=date(2025, 6, 1))
        assert sent == 1
        client.send_notification.assert_called_once()
        call_args = client.send_notification.call_args
        # Verify user_id is passed correctly (positional or keyword)
        assert call_args[1].get("user_id") == "user-1" or call_args[0][0] == "user-1"

    def test_notification_message_contains_task_info(self) -> None:
        store = TaskStore()
        task = Task(
            title="Report",
            due_date=date(2020, 6, 15),
            status="pending",
            assigned_user_id="user-1",
        )
        store.create(task)
        client = MagicMock()
        client.send_notification.return_value = {"id": "n1"}
        checker = OverdueChecker(store, client)
        checker.check(today=date(2025, 6, 1))

        call_kwargs = client.send_notification.call_args[1]
        assert "Report" in call_kwargs.get("message", "")
        assert call_kwargs.get("notification_type") == "overdue_task"

    def test_does_not_resend_notification(self) -> None:
        store = TaskStore()
        store.create(
            Task(
                title="Late",
                due_date=date(2020, 1, 1),
                status="pending",
                assigned_user_id="user-1",
            )
        )
        client = MagicMock()
        client.send_notification.return_value = {"id": "n1"}
        checker = OverdueChecker(store, client)

        checker.check(today=date(2025, 6, 1))
        sent = checker.check(today=date(2025, 6, 1))
        assert sent == 0

    def test_skips_task_without_assigned_user(self) -> None:
        store = TaskStore()
        store.create(
            Task(title="Late", due_date=date(2020, 1, 1), status="pending")
        )
        client = MagicMock()
        checker = OverdueChecker(store, client)
        sent = checker.check(today=date(2025, 6, 1))
        assert sent == 0
        client.send_notification.assert_not_called()

    def test_skips_completed_task(self) -> None:
        store = TaskStore()
        store.create(
            Task(
                title="Done",
                due_date=date(2020, 1, 1),
                status="completed",
                assigned_user_id="user-1",
            )
        )
        client = MagicMock()
        checker = OverdueChecker(store, client)
        sent = checker.check(today=date(2025, 6, 1))
        assert sent == 0

    def test_handles_client_error_gracefully(self) -> None:
        store = TaskStore()
        store.create(
            Task(
                title="Late",
                due_date=date(2020, 1, 1),
                status="pending",
                assigned_user_id="user-1",
            )
        )
        client = MagicMock()
        client.send_notification.side_effect = Exception("connection refused")
        checker = OverdueChecker(store, client)
        sent = checker.check(today=date(2025, 6, 1))
        assert sent == 0

    def test_multiple_overdue_tasks(self) -> None:
        store = TaskStore()
        store.create(
            Task(
                title="Task1",
                due_date=date(2020, 1, 1),
                status="pending",
                assigned_user_id="user-1",
            )
        )
        store.create(
            Task(
                title="Task2",
                due_date=date(2020, 6, 1),
                status="pending",
                assigned_user_id="user-2",
            )
        )
        client = MagicMock()
        client.send_notification.return_value = {"id": "n"}
        checker = OverdueChecker(store, client)
        sent = checker.check(today=date(2025, 6, 1))
        assert sent == 2
        assert client.send_notification.call_count == 2
