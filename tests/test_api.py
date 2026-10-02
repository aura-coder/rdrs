"""Tests for the FastAPI endpoints using TestClient."""
from fastapi.testclient import TestClient
from app.api.main import app
from app.database.models import init_db

client = TestClient(app)


def setup_module(module):
    init_db()


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_status():
    r = client.get('/status')
    assert r.status_code == 200
    body = r.json()
    assert 'level' in body
    assert 'score' in body


def test_alerts():
    r = client.get('/alerts')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_events():
    r = client.get('/events')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_reports():
    r = client.get('/reports')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_scan():
    r = client.post('/scan')
    assert r.status_code == 200


def test_settings():
    r = client.post('/settings')
    assert r.status_code == 200
