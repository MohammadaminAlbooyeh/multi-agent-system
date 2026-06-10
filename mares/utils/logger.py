"""Structured logger — thin wrapper around :mod:`structlog`."""

from __future__ import annotations

import logging
import sys

import structlog


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a configured structlog logger."""
    if not structlog.is_configured():
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO,
        )
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    return structlog.get_logger(name)


__all__ = ["get_logger"]
