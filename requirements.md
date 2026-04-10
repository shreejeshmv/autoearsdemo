# Requirements — Add Due Date to Tasks

## EARS-Notation Requirements

- **REQ-001** (Ubiquitous): The task-service shall store a `due_date` field (date-only, ISO 8601 format YYYY-MM-DD) for each task.
- **REQ-002** (Ubiquitous): The task-service API shall accept an optional `due_date` parameter (ISO 8601 date, YYYY-MM-DD) when creating a task.
- **REQ-003** (Ubiquitous): The task-service API shall accept an optional `due_date` parameter (ISO 8601 date, YYYY-MM-DD) when updating a task.
- **REQ-004** (Ubiquitous): The task-service API shall return the `due_date` field (or `null` if unset) in all task response payloads (single-task and list endpoints).
- **REQ-005** (Event-Driven): When a task's `due_date` is earlier than the current date and the task status is not `"completed"`, the system shall include an `is_overdue: true` flag in the task response.
- **REQ-006** (Event-Driven): When a task list is requested with `sort_by=due_date`, the system shall order results by due date ascending with nulls last.
- **REQ-007** (State-Driven): While a task has a `due_date` that is earlier than the current date and the task status is not `"completed"`, the task shall be considered overdue.
- **REQ-008** (Ubiquitous): The `due_date` field shall be nullable, allowing tasks to exist without a due date.
- **REQ-009** (Unwanted Behavior): If a task is created or updated with a `due_date` value that is not a valid ISO 8601 date (YYYY-MM-DD), then the system shall return a 400 Bad Request error with a descriptive message.
- **REQ-010** (Event-Driven): When a task becomes overdue (due_date passes and status is not `"completed"`), the task-service shall call the user-service notification endpoint to notify the assigned user.
- **REQ-011** (Ubiquitous): The user-service shall expose a `POST /notifications` endpoint that accepts a `user_id`, `message`, and `notification_type`, and stores the notification.
- **REQ-012** (Ubiquitous): The user-service shall expose a `GET /notifications/{user_id}` endpoint to retrieve notifications for a user.
- **REQ-013** (Event-Driven): When a task list is requested with a `due_before` query parameter, the system shall return only tasks with a `due_date` on or before the specified date.
- **REQ-014** (Event-Driven): When a task list is requested with a `due_after` query parameter, the system shall return only tasks with a `due_date` on or after the specified date.
- **REQ-015** (Event-Driven): When a task list is requested with an `overdue=true` query parameter, the system shall return only tasks that are overdue (due_date before today and status is not `"completed"`).
