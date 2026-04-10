"""Priority constants and validation for the task-service."""

from enum import Enum
from typing import Optional


class Priority(str, Enum):
    """Allowed priority levels for tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


VALID_PRIORITIES = {p.value for p in Priority}
DEFAULT_PRIORITY = Priority.MEDIUM.value


def validate_priority(value: Optional[str]) -> Optional[str]:
    """Validate a priority value.

    Args:
        value: The priority string to validate.

    Returns:
        The validated priority string, or None if value is None.

    Raises:
        ValueError: If the value is not a valid priority.
    """
    if value is None:
        return None
    if value not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority '{value}'. "
            f"Allowed values: {', '.join(sorted(VALID_PRIORITIES))}"
        )
    return value
