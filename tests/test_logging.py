"""Tests for logging setup."""
from app.core.logging import setup_logging


def test_setup_logging_returns_logger():
    logger = setup_logging()
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
