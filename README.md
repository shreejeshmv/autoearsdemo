# Task Priority Demo App

A demo microservices application with **task-service** and **user-service**.

## Features

- Create, read, update, delete, and list tasks
- Task priority field (`low`, `medium`, `high`) with `medium` as default
- Filter tasks by priority
- User management via user-service
- One-time migration script to backfill priority for existing tasks

## Running

```bash
pip install flask
# Start task-service
python task-service/app.py
# Start user-service
python user-service/app.py
```

## Testing

```bash
pip install pytest
pytest
```
