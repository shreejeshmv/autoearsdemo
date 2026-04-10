"""Tests for task-service store."""

from datetime import date

from task_service.models import Task
from task_service.store import TaskStore


class TestTaskStore:
    """Tests for TaskStore CRUD and query operations."""

    def _make_store(self) -> TaskStore:
        return TaskStore()

    # -- CRUD -----------------------------------------------------------------

    def test_create_and_get(self) -> None:
        store = self._make_store()
        task = Task(title="A")
        store.create(task)
        assert store.get(task.id) is task

    def test_get_missing_returns_none(self) -> None:
        store = self._make_store()
        assert store.get("no-such-id") is None

    def test_update_existing(self) -> None:
        store = self._make_store()
        task = Task(title="A")
        store.create(task)
        updated = store.update(task.id, title="B", due_date=date(2025, 12, 1))
        assert updated is not None
        assert updated.title == "B"
        assert updated.due_date == date(2025, 12, 1)

    def test_update_missing_returns_none(self) -> None:
        store = self._make_store()
        assert store.update("nope", title="X") is None

    def test_delete(self) -> None:
        store = self._make_store()
        task = Task(title="A")
        store.create(task)
        assert store.delete(task.id) is True
        assert store.get(task.id) is None

    def test_delete_missing_returns_false(self) -> None:
        store = self._make_store()
        assert store.delete("nope") is False

    # -- Filtering ------------------------------------------------------------

    def test_filter_due_before(self) -> None:
        store = self._make_store()
        store.create(Task(title="A", due_date=date(2025, 1, 1)))
        store.create(Task(title="B", due_date=date(2025, 6, 1)))
        store.create(Task(title="C", due_date=date(2025, 12, 1)))
        tasks = store.list_tasks(due_before=date(2025, 6, 1))
        titles = {t.title for t in tasks}
        assert titles == {"A", "B"}

    def test_filter_due_after(self) -> None:
        store = self._make_store()
        store.create(Task(title="A", due_date=date(2025, 1, 1)))
        store.create(Task(title="B", due_date=date(2025, 6, 1)))
        store.create(Task(title="C", due_date=date(2025, 12, 1)))
        tasks = store.list_tasks(due_after=date(2025, 6, 1))
        titles = {t.title for t in tasks}
        assert titles == {"B", "C"}

    def test_filter_overdue(self) -> None:
        store = self._make_store()
        store.create(Task(title="Overdue", due_date=date(2020, 1, 1), status="pending"))
        store.create(Task(title="Done", due_date=date(2020, 1, 1), status="completed"))
        store.create(Task(title="Future", due_date=date(2099, 1, 1), status="pending"))
        store.create(Task(title="No date", status="pending"))
        tasks = store.list_tasks(overdue=True, today=date(2025, 6, 1))
        assert len(tasks) == 1
        assert tasks[0].title == "Overdue"

    def test_filter_due_before_excludes_null_due_dates(self) -> None:
        store = self._make_store()
        store.create(Task(title="No date"))
        store.create(Task(title="Has date", due_date=date(2025, 1, 1)))
        tasks = store.list_tasks(due_before=date(2025, 12, 31))
        assert len(tasks) == 1
        assert tasks[0].title == "Has date"

    def test_filter_due_after_excludes_null_due_dates(self) -> None:
        store = self._make_store()
        store.create(Task(title="No date"))
        store.create(Task(title="Has date", due_date=date(2025, 6, 1)))
        tasks = store.list_tasks(due_after=date(2025, 1, 1))
        assert len(tasks) == 1
        assert tasks[0].title == "Has date"

    def test_filter_date_range(self) -> None:
        """Combining due_after and due_before gives a date range."""
        store = self._make_store()
        store.create(Task(title="A", due_date=date(2025, 1, 1)))
        store.create(Task(title="B", due_date=date(2025, 6, 1)))
        store.create(Task(title="C", due_date=date(2025, 12, 1)))
        tasks = store.list_tasks(
            due_after=date(2025, 3, 1),
            due_before=date(2025, 9, 1),
        )
        assert len(tasks) == 1
        assert tasks[0].title == "B"

    # -- Sorting --------------------------------------------------------------

    def test_sort_by_due_date_ascending_nulls_last(self) -> None:
        store = self._make_store()
        store.create(Task(title="No date"))
        store.create(Task(title="Later", due_date=date(2025, 12, 1)))
        store.create(Task(title="Earlier", due_date=date(2025, 1, 1)))
        tasks = store.list_tasks(sort_by="due_date")
        titles = [t.title for t in tasks]
        assert titles == ["Earlier", "Later", "No date"]

    def test_sort_by_due_date_with_filter(self) -> None:
        """Sorting and filtering can be combined."""
        store = self._make_store()
        store.create(Task(title="A", due_date=date(2025, 6, 1)))
        store.create(Task(title="B", due_date=date(2025, 1, 1)))
        store.create(Task(title="C", due_date=date(2025, 12, 1)))
        tasks = store.list_tasks(
            sort_by="due_date",
            due_before=date(2025, 7, 1),
        )
        titles = [t.title for t in tasks]
        assert titles == ["B", "A"]

    # -- Overdue helpers ------------------------------------------------------

    def test_get_overdue_tasks(self) -> None:
        store = self._make_store()
        store.create(Task(title="Overdue", due_date=date(2020, 1, 1), status="pending"))
        store.create(Task(title="Done", due_date=date(2020, 1, 1), status="completed"))
        store.create(Task(title="Future", due_date=date(2099, 1, 1), status="pending"))
        overdue = store.get_overdue_tasks(today=date(2025, 6, 1))
        assert len(overdue) == 1
        assert overdue[0].title == "Overdue"

    def test_get_overdue_tasks_excludes_no_due_date(self) -> None:
        store = self._make_store()
        store.create(Task(title="No date", status="pending"))
        overdue = store.get_overdue_tasks(today=date(2025, 6, 1))
        assert len(overdue) == 0
