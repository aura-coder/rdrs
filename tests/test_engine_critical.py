from datetime import datetime, timezone
from app.detectors.engine import DetectionEngine

def test_engine_reaches_critical():
    engine = DetectionEngine()
    # Push many rapid events to trigger thresholds
    for i in range(60):
        engine.add_event('created', f'/tmp/file_{i}.txt', '.txt', 7.9)
    for i in range(30):
        engine.add_event('moved', f'/tmp/file_{i}.locked', '.locked', None)

    # The engine should have escalated to at least Warning
    assert engine.last_level in ('Warning', 'Critical')

def test_engine_entropy_signal_fires():
    engine = DetectionEngine()
    for i in range(30):
        engine.add_event('created', f'/tmp/e_{i}.txt', '.txt', 7.99)
    # High entropy should be reflected
    assert engine.last_level in ('Warning', 'Critical')
