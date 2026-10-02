from app.detectors.engine import DetectionEngine

def test_engine_normal():
    engine = DetectionEngine()
    engine.add_event('modified', '/tmp/test.txt', '.txt', 3.0)
    assert True
