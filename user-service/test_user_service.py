"""Tests for the user-service."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import store
from handler import (
    handle_create_user,
    handle_delete_user,
    handle_get_user,
    handle_list_users,
    handle_update_user,
)


class TestUserStore:
    """Tests for user store CRUD operations."""

    def setup_method(self) -> None:
        store.clear_all()

    def test_create_user(self) -> None:
        user = store.create_user(name="Alice", email="alice@example.com")
        assert user["name"] == "Alice"
        assert user["email"] == "alice@example.com"
        assert "id" in user

    def test_get_user(self) -> None:
        user = store.create_user(name="Bob")
        fetched = store.get_user(user["id"])
        assert fetched == user

    def test_get_user_not_found(self) -> None:
        assert store.get_user("bad") is None

    def test_list_users(self) -> None:
        store.create_user(name="A")
        store.create_user(name="B")
        assert len(store.get_all_users()) == 2

    def test_update_user(self) -> None:
        user = store.create_user(name="Old")
        updated = store.update_user(user["id"], {"name": "New"})
        assert updated is not None
        assert updated["name"] == "New"

    def test_delete_user(self) -> None:
        user = store.create_user(name="Del")
        assert store.delete_user(user["id"]) is True
        assert store.get_user(user["id"]) is None


class TestUserHandlers:
    """Tests for user-service handlers."""

    def setup_method(self) -> None:
        store.clear_all()

    def test_create_user_success(self) -> None:
        body, status = handle_create_user({"name": "Alice"})
        assert status == 201
        assert body["name"] == "Alice"

    def test_create_user_missing_name(self) -> None:
        body, status = handle_create_user({})
        assert status == 400

    def test_list_users(self) -> None:
        handle_create_user({"name": "A"})
        body, status = handle_list_users()
        assert status == 200
        assert len(body) == 1

    def test_get_user(self) -> None:
        created, _ = handle_create_user({"name": "A"})
        body, status = handle_get_user(created["id"])
        assert status == 200
        assert body["name"] == "A"

    def test_get_user_not_found(self) -> None:
        body, status = handle_get_user("bad")
        assert status == 404

    def test_update_user(self) -> None:
        created, _ = handle_create_user({"name": "Old"})
        body, status = handle_update_user(created["id"], {"name": "New"})
        assert status == 200
        assert body["name"] == "New"

    def test_update_user_not_found(self) -> None:
        body, status = handle_update_user("bad", {"name": "X"})
        assert status == 404

    def test_delete_user(self) -> None:
        created, _ = handle_create_user({"name": "Del"})
        body, status = handle_delete_user(created["id"])
        assert status == 200

    def test_delete_user_not_found(self) -> None:
        body, status = handle_delete_user("bad")
        assert status == 404
