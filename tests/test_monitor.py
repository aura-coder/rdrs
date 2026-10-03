"""Tests for the file-system monitor handler (fully mocked, no watchdog)."""
from unittest.mock import MagicMock, patch

import pytest

from app.detectors.monitor import RansomwareEventHandler


class FakeEvent:
    def __init__(self, src_path, is_directory=False, dest_path=None):
        self.src_path = src_path
        self.dest_path = dest_path
        self.is_directory = is_directory


@pytest.fixture
def engine():
    m = MagicMock()
    m.add_event = MagicMock()
    return m


@pytest.fixture
def handler(engine):
    return RansomwareEventHandler(engine)


def test_skips_directories(handler, engine):
    handler.on_created(FakeEvent('/tmp/x', is_directory=True))
    handler.on_deleted(FakeEvent('/tmp/x', is_directory=True))
    assert engine.add_event.call_count == 0


def test_on_created_emits_event(handler, engine, tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello world")
    with patch("app.detectors.monitor.add_file_event"), \
         patch("app.detectors.monitor.add_process_snapshot"), \
         patch("app.detectors.monitor.get_process_info", return_value=None), \
         patch("app.detectors.monitor.file_entropy", return_value=3.14):
        handler.on_created(FakeEvent(str(f)))
    assert engine.add_event.call_count == 1
    args = engine.add_event.call_args[0]
    assert args[0] == 'created'
    assert args[2] == '.txt'


def test_on_moved_reads_destination(handler, engine, tmp_path):
    src = tmp_path / "a.txt"
    dst = tmp_path / "a.locked"
    dst.write_bytes(b"x" * 1000)
    with patch("app.detectors.monitor.add_file_event"), \
         patch("app.detectors.monitor.add_process_snapshot"), \
         patch("app.detectors.monitor.get_process_info", return_value=None), \
         patch("app.detectors.monitor.file_entropy", return_value=7.99):
        handler.on_moved(FakeEvent(str(src), dest_path=str(dst)))
    assert engine.add_event.call_count == 1
    args = engine.add_event.call_args[0]
    assert args[0] == 'moved'
    assert args[1].endswith('.locked')


def test_on_closed_emits_modified(handler, engine, tmp_path):
    f = tmp_path / "b.txt"
    f.write_text("data" * 10)
    with patch("app.detectors.monitor.add_file_event"), \
         patch("app.detectors.monitor.add_process_snapshot"), \
         patch("app.detectors.monitor.get_process_info", return_value=None), \
         patch("app.detectors.monitor.file_entropy", return_value=4.2):
        handler.on_closed(FakeEvent(str(f)))
    assert engine.add_event.call_count == 1
    assert engine.add_event.call_args[0][0] == 'modified'


def test_dedup_suppresses_duplicate(handler, engine):
    with patch("app.detectors.monitor.add_file_event"), \
         patch("app.detectors.monitor.add_process_snapshot"), \
         patch("app.detectors.monitor.get_process_info", return_value=None):
        handler.on_deleted(FakeEvent('/tmp/x.txt'))
        handler.on_deleted(FakeEvent('/tmp/x.txt'))
    assert engine.add_event.call_count == 1
