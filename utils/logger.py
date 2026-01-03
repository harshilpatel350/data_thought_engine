"""
Structured logging helper using the standard `logging` module.
Provides a small factory producing loggers that emit JSON-like records.
"""
from __future__ import annotations

import logging
import json
from typing import Any, Dict


class StructuredLogger:
    """Lightweight structured logger that formats records as JSON strings.

    Avoids external dependencies while producing predictable machine-readable
    output useful for production systems.
    """

    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            self._logger.addHandler(handler)
            self._logger.propagate = False
        self._logger.setLevel(logging.INFO)

    def _format(self, level: str, message: str, extra: Dict[str, Any] | None = None) -> str:
        payload = {"level": level, "message": message}
        if extra:
            payload.update(extra)
        return json.dumps(payload, default=str)

    def info(self, message: str, extra: Dict[str, Any] | None = None) -> None:
        self._logger.info(self._format("info", message, extra))

    def warn(self, message: str, extra: Dict[str, Any] | None = None) -> None:
        self._logger.warning(self._format("warning", message, extra))

    def error(self, message: str, extra: Dict[str, Any] | None = None) -> None:
        self._logger.error(self._format("error", message, extra))


def get_logger(name: str) -> StructuredLogger:
    """Factory for obtaining a structured logger instance.

    Keeps logging configuration centralized and deterministic.
    """
    return StructuredLogger(name)
