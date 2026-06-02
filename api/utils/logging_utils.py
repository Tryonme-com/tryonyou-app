"""
Structured logging helper.

Call setup_logging() once at app/worker startup so that all loggers in the
process emit consistent, safe output.

Sensitive data rules:
- never log full raw payloads
- never log API keys or secrets
- truncate error messages to 500 chars before logging
"""
from __future__ import annotations

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Configure root logger with a timestamped format.

    Args:
        level: One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
               Defaults to INFO if the value is unrecognised.
    """
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric,
        format="%(asctime)s %(levelname)-8s %(name)-30s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("stripe").setLevel(logging.WARNING)
