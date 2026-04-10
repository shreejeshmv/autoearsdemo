"""Tests for user-service store."""

from user_service.models import Notification, User
from user_service.store import NotificationStore, UserStore


class TestUserStore:
    def test_create_and_get(self) -> None:
        store = UserStore()
        user = User(name="Alice")
        store.create(user)
        assert store.get(user.id) is user

    def test_get_missing(self) -> None:
        store = UserStore()
        assert store.get("no") is None

    def test_list_users(self) -> None:
        store = UserStore()
        store.create(User(name="A"))
        store.create(User(name="B"))
        assert len(store.list_users()) == 2


class TestNotificationStore:
    def test_create_and_get_by_user(self) -> None:
        store = NotificationStore()
        n1 = Notification(user_id="u1", message="M1")
        n2 = Notification(user_id="u1", message="M2")
        n3 = Notification(user_id="u2", message="M3")
        store.create(n1)
        store.create(n2)
        store.create(n3)
        user1_notifs = store.get_by_user("u1")
        assert len(user1_notifs) == 2
        assert all(n.user_id == "u1" for n in user1_notifs)

    def test_get_by_user_empty(self) -> None:
        store = NotificationStore()
        assert store.get_by_user("nobody") == []

    def test_notifications_ordered_newest_first(self) -> None:
        """Notifications should be returned newest first."""
        store = NotificationStore()
        n1 = Notification(user_id="u1", message="First")
        n2 = Notification(user_id="u1", message="Second")
        store.create(n1)
        store.create(n2)
        result = store.get_by_user("u1")
        # n2 was created after n1, so it should appear first
        assert result[0].message == "Second"
        assert result[1].message == "First"
