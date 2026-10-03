"""Extra engine tests: quarantine, process helpers, thresholds."""
from app.detectors.engine import DetectionEngine


def test_latest_cpu_no_snapshots_returns_zero():
    e = DetectionEngine()
    # Should not raise even if no snapshots exist
    assert e._latest_cpu() >= 0.0


def test_suspect_name_no_snapshots_returns_str():
    e = DetectionEngine()
    assert isinstance(e._suspect_name(), str)


def test_quarantine_copies_file(tmp_path):
    e = DetectionEngine()
    e.quarantine_path = str(tmp_path / "q")
    src = tmp_path / "victim.txt"
    src.write_text("payload")
    copied = e._quarantine_files([str(src)])
    assert copied == 1
    assert (tmp_path / "q" / "victim.txt").read_text() == "payload"
    # Original must remain untouched
    assert src.read_text() == "payload"


def test_quarantine_skips_missing():
    e = DetectionEngine()
    copied = e._quarantine_files(["/tmp/definitely_not_here_zzz.txt"])
    assert copied == 0


def test_quarantine_dedup_on_name_collision(tmp_path):
    e = DetectionEngine()
    e.quarantine_path = str(tmp_path / "q")
    src = tmp_path / "dup.txt"
    src.write_text("one")
    e._quarantine_files([str(src)])
    # Write new content, quarantine again — should get a "_1" suffix
    src.write_text("two")
    copied = e._quarantine_files([str(src)])
    assert copied == 1
    files = sorted((tmp_path / "q").iterdir())
    assert len(files) == 2


def test_score_below_all_thresholds_is_normal():
    e = DetectionEngine()
    e.add_event('modified', '/tmp/a.txt', '.txt', 1.0)
    assert e.last_level == 'Normal'


def test_weights_include_new_signals():
    e = DetectionEngine()
    assert e.weights.get('extension_changes', 0) > 0
    assert e.weights.get('cpu_spike', 0) > 0
    assert e.weights.get('unknown_process', 0) > 0
