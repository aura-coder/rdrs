"""Tests for the entry point — all external calls mocked."""
from unittest.mock import patch

import app.main


def test_main_bootstraps_and_starts():
    with patch("app.main.setup_logging") as log, \
         patch("app.main.init_db") as db, \
         patch("app.main.threading.Thread") as thread_cls, \
         patch("app.main.uvicorn.run") as uvi:
        app.main.main()
        log.assert_called_once()
        db.assert_called_once()
        thread_cls.assert_called_once()
        uvi.assert_called_once()
