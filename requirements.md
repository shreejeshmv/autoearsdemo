# Requirements — Add Priority Field to Task Service

## EARS-Notation Requirements

| ID | Pattern | Requirement |
|----|---------|-------------|
| REQ-001 | Ubiquitous | The task-service shall support a `priority` field on tasks with allowed values of `low`, `medium`, and `high`. |
| REQ-002 | Event-driven | When a task is created without an explicit `priority` value, the system shall default the priority to `medium`. |
| REQ-003 | Event-driven | When a client provides an invalid `priority` value during task creation or update, the system shall return a 400 status code with an error message listing the allowed values. |
| REQ-004 | Ubiquitous | The `priority` field shall be included in all task responses (create, get, list, update). |
| REQ-005 | Event-driven | When a `priority` query parameter is provided on `GET /tasks`, the system shall return only tasks matching that priority value. |
| REQ-006 | Event-driven | When a `priority` query parameter with an invalid value is provided on `GET /tasks`, the system shall return a 400 status code with an error message. |
| REQ-007 | Event-driven | When a task is updated via `PUT /tasks/<task_id>` with a valid `priority` field, the system shall persist the new priority value. |
| REQ-008 | Event-driven | When the migration script is executed, all existing tasks without a priority value shall be backfilled with a priority of `medium`. |

## Implementation Notes

- **Priority enum**: Defined in `task-service/priority.py` with `Priority.LOW`, `Priority.MEDIUM`, `Priority.HIGH`.
- **Validation**: `validate_priority()` in `task-service/priority.py` raises `ValueError` for invalid inputs.
- **Default**: `DEFAULT_PRIORITY = "medium"` applied at task creation in `task-service/store.py`.
- **Filtering**: `GET /tasks?priority=<value>` filters in-memory store via `store.get_all_tasks(priority_filter=...)`.
- **Migration**: `task-service/migrate_priority.py` backfills legacy tasks missing the priority field.
- **User-service**: No changes required; user-service remains a standalone CRUD service for users.
