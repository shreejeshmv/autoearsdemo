# User Service

A lightweight Flask REST API for managing users.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users` | List all users |
| POST | `/users` | Create a new user |
| GET | `/users/<id>` | Retrieve a single user |
| PUT | `/users/<id>` | Update a user |
| DELETE | `/users/<id>` | Delete a user |
| GET | `/users/<id>/tasks` | List tasks assigned to a user (proxies to task-service) |

## User Schema

```json
{
  "id": "string (UUID)",
  "name": "string",
  "email": "string",
  "created_at": "ISO 8601 datetime"
}
```
