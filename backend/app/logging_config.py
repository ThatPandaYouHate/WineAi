"""Centralised logging configuration."""
from __future__ import annotations

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a sensible default formatter."""
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. uvicorn reload); just adjust level.
        root.setLevel(level.upper())
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(level.upper())

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
