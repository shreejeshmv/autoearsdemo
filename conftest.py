"""Workspace-level conftest — ensures both service packages are importable."""

import pathlib
import sys

_workspace = pathlib.Path(__file__).resolve().parent

for service_dir in ("task-service", "user-service"):
    p = str(_workspace / service_dir)
    if p not in sys.path:
        sys.path.insert(0, p)
