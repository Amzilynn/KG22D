"""Logging helpers."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a configured project logger."""
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
