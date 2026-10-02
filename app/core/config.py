import yaml
from pathlib import Path

def load_config(path="config.yaml"):
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file {path} not found")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
