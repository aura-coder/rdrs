from app.core.entropy import shannon_entropy

def test_entropy_empty():
    assert shannon_entropy(b'') == 0.0

def test_entropy_uniform():
    data = bytes([0]*100)
    assert shannon_entropy(data) == 0.0

def test_entropy_random():
    import os
    data = os.urandom(1000)
    ent = shannon_entropy(data)
    assert 7.0 < ent <= 8.0


def test_file_entropy_on_real_file(tmp_path):
    from app.core.entropy import file_entropy
    f = tmp_path / "sample.txt"
    f.write_text("hello world " * 100)
    ent = file_entropy(str(f))
    assert 0.0 <= ent <= 8.0


def test_file_entropy_on_missing_file():
    from app.core.entropy import file_entropy
    ent = file_entropy("/tmp/this/does/not/exist_xyz_123")
    assert ent == 0.0
