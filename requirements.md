# Requirements — Add Due Date to Task Service

## EARS-Notation Requirements

- **REQ-001** (Ubiquitous): Each task **shall** have an optional `due_date` field represented as an ISO 8601 date-only value (`YYYY-MM-DD`).

- **REQ-002** (Ubiquitous): The task service API **shall** accept a `due_date` field when creating a new task.

- **REQ-003** (Ubiquitous): The task service API **shall** accept a `due_date` field when updating an existing task.

- **REQ-004** (Ubiquitous): The task service API **shall** return the `due_date` field (or `null` if unset) in all task response payloads (single-task and list endpoints).

- **REQ-005** (Event-Driven): **When** a task is retrieved, the response **shall** include an `overdue` boolean flag that is `true` if the `due_date` is before today's date in UTC and the task status is not `completed`, and `false` otherwise.

- **REQ-006** (State-Driven): **While** a task has no `due_date` set, the `overdue` flag **shall** be `false`.

- **REQ-007** (Ubiquitous): The task data store **shall** persist the `due_date` field so that it survives service restarts.

- **REQ-008** (Event-Driven): **When** a `due_date` value is provided that is not a valid date or is not in `YYYY-MM-DD` format, the task service **shall** return a `400 Bad Request` error with a descriptive message.

- **REQ-009** (Ubiquitous): Existing tasks created before the due-date feature **shall** default to a `null` due date and remain fully accessible.

- **REQ-010** (Event-Driven): **When** a client requests the task list with a `?overdue=true` query parameter, the system **shall** return only tasks whose `due_date` is in the past (before today in UTC) and whose status is not `completed`.

## Design Decisions

| Decision | Choice |
|---|---|
| Date granularity | Date-only (`YYYY-MM-DD`) |
| Overdue semantics | `due_date < today (UTC)` — a task is overdue starting the day after its due date |
| Date-range filtering | Not supported |
| Sorting by due date | Not supported |
| Notifications | Not supported |
| Timezone | All comparisons in UTC |
