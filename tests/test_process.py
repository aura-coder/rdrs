"""Tests for process snapshot helper."""
import os
from app.core.process import get_process_info


def test_get_process_info_current():
    info = get_process_info(os.getpid())
    assert info is not None
    assert info['pid'] == os.getpid()
    assert 'name' in info
    assert 'executable' in info


def test_get_process_info_invalid_pid():
    # PID 999999 should not exist
    info = get_process_info(999999)
    assert info is None
