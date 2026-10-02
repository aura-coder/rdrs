"""Tests for database CRUD operations."""
from app.database.crud import (
    add_file_event,
    add_process_snapshot,
    add_alert,
    add_incident,
    get_recent_alerts,
    get_recent_events,
    get_incidents,
)
from app.database.models import init_db


def setup_module(module):
    init_db()


def test_add_file_event_and_fetch():
    add_file_event('created', '/tmp/x.txt', '.txt', 3.5)
    events = get_recent_events(limit=5)
    assert isinstance(events, list)
    assert len(events) >= 1
    assert 'event_type' in events[0]
    assert 'path' in events[0]


def test_add_alert_and_fetch():
    add_alert('Warning', 45, 'unit test alert')
    alerts = get_recent_alerts(limit=5)
    assert isinstance(alerts, list)
    assert any(a['message'] == 'unit test alert' for a in alerts)


def test_add_incident_and_fetch():
    add_incident(80, 'Critical', ['/tmp/a.txt'], {'pid': 1, 'name': 'test'})
    incs = get_incidents(limit=5)
    assert isinstance(incs, list)
    assert incs[0]['level'] == 'Critical'
    assert incs[0]['score'] == 80


def test_add_process_snapshot_with_none():
    # Should silently ignore None without raising
    add_process_snapshot(None)


def test_add_process_snapshot_with_data():
    add_process_snapshot({
        'pid': 99999,
        'name': 'pytest-proc',
        'cpu_percent': 0.0,
        'memory_percent': 0.1,
        'disk_writes': 0,
        'executable': '/bin/pytest',
        'parent_pid': 1,
    })
