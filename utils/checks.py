"""
Assertion helpers and invariants used across the system.
Raising explicit, descriptive errors to signal failure conditions.
"""
from __future__ import annotations

import os
from typing import Any


def assert_path_exists(path: str) -> None:
    """Raise an error if a filesystem path does not exist.

    This avoids later opaque I/O errors and keeps failures explicit.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")


def assert_is_csv(path: str) -> None:
    """Ensure file path looks like a CSV file by extension.

    This is a lightweight check; reading/parsing is performed elsewhere.
    """
    if not path.lower().endswith('.csv'):
        raise ValueError(f"Expected a .csv file: {path}")


def assert_non_empty(value: Any, name: str) -> None:
    """Ensure a configuration value or collection is not empty.

    Keeps errors descriptive for callers.
    """
    if not value:
        raise ValueError(f"Required value '{name}' is empty or falsy")
