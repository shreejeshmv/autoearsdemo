"""One-time migration script to backfill priority for existing tasks.

Run this script at deployment time to set 'priority' to 'medium'
for all tasks that do not already have a priority value.

Usage:
    python migrate_priority.py
"""

import store
from priority import DEFAULT_PRIORITY


def backfill_priority() -> int:
    """Set priority to DEFAULT_PRIORITY for tasks missing the field.

    Returns:
        The number of tasks that were updated.
    """
    updated = 0
    for task in store.get_all_tasks():
        if not task.get("priority"):
            task["priority"] = DEFAULT_PRIORITY
            updated += 1
    return updated


if __name__ == "__main__":
    count = backfill_priority()
    print(f"Migration complete: {count} task(s) backfilled with priority '{DEFAULT_PRIORITY}'.")
