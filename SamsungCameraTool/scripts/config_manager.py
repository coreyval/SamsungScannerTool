import json, os
from .utils import ensure_dir, base_dir

CONFIG_PATH = os.path.join(base_dir(), "config.json")
DEFAULT_SAVE_DIR = os.path.join(base_dir(), "captures")

def load_config():
    # Create default if missing
    if not os.path.exists(CONFIG_PATH):
        cfg = {"save_dir": DEFAULT_SAVE_DIR}
        save_config(cfg)
        ensure_dir(DEFAULT_SAVE_DIR)
        return cfg
    # Load existing
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    # Harden values
    save_dir = cfg.get("save_dir") or DEFAULT_SAVE_DIR
    ensure_dir(save_dir)
    cfg["save_dir"] = save_dir
    return cfg

def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
