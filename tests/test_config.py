from app.core.config import load_config

def test_load_config_returns_dict():
    cfg = load_config()
    assert isinstance(cfg, dict)
    assert 'watch_folders' in cfg
    assert 'thresholds' in cfg
    assert 'weights' in cfg

def test_load_config_thresholds():
    cfg = load_config()
    assert cfg['thresholds']['files_per_minute'] > 0
    assert cfg['thresholds']['entropy_avg'] > 0

def test_load_config_weights_sum():
    cfg = load_config()
    total = sum(cfg['weights'].values())
    # Weights should be meaningful; total must be > 0
    assert total > 0
