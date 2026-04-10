"""Flask application for the task-service."""

from flask import Flask, jsonify, request

from handler import (
    handle_create_task,
    handle_delete_task,
    handle_get_task,
    handle_list_tasks,
    handle_update_task,
)

app = Flask(__name__)


@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task."""
    body = request.get_json(force=True, silent=True) or {}
    response, status = handle_create_task(body)
    return jsonify(response), status


@app.route("/tasks", methods=["GET"])
def list_tasks():
    """List all tasks, with optional priority filter."""
    response, status = handle_list_tasks(dict(request.args))
    return jsonify(response), status


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id: str):
    """Get a single task by ID."""
    response, status = handle_get_task(task_id)
    return jsonify(response), status


@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id: str):
    """Update a task by ID."""
    body = request.get_json(force=True, silent=True) or {}
    response, status = handle_update_task(task_id, body)
    return jsonify(response), status


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id: str):
    """Delete a task by ID."""
    response, status = handle_delete_task(task_id)
    return jsonify(response), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
