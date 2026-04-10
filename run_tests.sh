#!/usr/bin/env bash
set -e
pip install flask pytest requests 2>/dev/null
cd /tmp/workspace/task-service && python -m pytest -v test_app.py
cd /tmp/workspace/user-service && python -m pytest -v test_app.py
