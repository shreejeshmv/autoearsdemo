# Task Service

A lightweight Flask REST API for managing tasks with due-date support.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks` | List all tasks (supports `?overdue=true` filter) |
| POST | `/tasks` | Create a new task |
| GET | `/tasks/<id>` | Retrieve a single task |
| PUT | `/tasks/<id>` | Update a task |
| DELETE | `/tasks/<id>` | Delete a task |

## Task Schema

```json
{
  "id": "string (UUID)",
  "title": "string",
  "description": "string | null",
  "status": "pending | in_progress | completed",
  "due_date": "YYYY-MM-DD | null",
  "overdue": "boolean (computed)",
  "assignee_id": "string | null",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```
