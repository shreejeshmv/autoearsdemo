"""Flask application for the user-service."""

from flask import Flask, jsonify, request

from handler import (
    handle_create_user,
    handle_delete_user,
    handle_get_user,
    handle_list_users,
    handle_update_user,
)

app = Flask(__name__)


@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user."""
    body = request.get_json(force=True, silent=True) or {}
    response, status = handle_create_user(body)
    return jsonify(response), status


@app.route("/users", methods=["GET"])
def list_users():
    """List all users."""
    response, status = handle_list_users()
    return jsonify(response), status


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id: str):
    """Get a single user by ID."""
    response, status = handle_get_user(user_id)
    return jsonify(response), status


@app.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    """Update a user by ID."""
    body = request.get_json(force=True, silent=True) or {}
    response, status = handle_update_user(user_id, body)
    return jsonify(response), status


@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id: str):
    """Delete a user by ID."""
    response, status = handle_delete_user(user_id)
    return jsonify(response), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
