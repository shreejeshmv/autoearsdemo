"""conftest for user-service tests — ensures user_service is importable."""

import pathlib
import sys

# Add the user-service directory to sys.path so 'user_service' package resolves.
_service_dir = str(pathlib.Path(__file__).resolve().parent.parent)
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)
