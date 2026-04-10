"""Tests for priority module."""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(__file__))

from priority import Priority, VALID_PRIORITIES, DEFAULT_PRIORITY, validate_priority


class TestPriorityEnum:
    """Tests for the Priority enum (REQ-001)."""

    def test_priority_has_exactly_three_values(self) -> None:
        assert len(Priority) == 3

    def test_priority_values(self) -> None:
        assert Priority.LOW.value == "low"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.HIGH.value == "high"

    def test_valid_priorities_set(self) -> None:
        assert VALID_PRIORITIES == {"low", "medium", "high"}

    def test_default_priority_is_medium(self) -> None:
        assert DEFAULT_PRIORITY == "medium"


class TestValidatePriority:
    """Tests for validate_priority (REQ-006)."""

    def test_valid_low(self) -> None:
        assert validate_priority("low") == "low"

    def test_valid_medium(self) -> None:
        assert validate_priority("medium") == "medium"

    def test_valid_high(self) -> None:
        assert validate_priority("high") == "high"

    def test_none_returns_none(self) -> None:
        assert validate_priority(None) is None

    def test_invalid_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid priority 'critical'"):
            validate_priority("critical")

    def test_empty_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid priority ''"):
            validate_priority("")

    def test_case_sensitive(self) -> None:
        with pytest.raises(ValueError, match="Invalid priority 'High'"):
            validate_priority("High")
