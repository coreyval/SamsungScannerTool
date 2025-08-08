import json
import os
from file_utils import get_paths, ensure_folder_exists

BASE_DIR, TOOLS_DIR, CAPTURE_DIR, TEMP_VIEW_DIR = get_paths()
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def ensure_config_initialized(default_save_dir: str):
    if not os.path.exists(CONFIG_FILE):
        ensure_folder_exists(default_save_dir)
        data = {"save_folder": default_save_dir}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

def _load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_config(data: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_save_folder() -> str:
    cfg = _load_config()
    path = cfg.get("save_folder", "")
    if not path:
        return CAPTURE_DIR
    ensure_folder_exists(path)
    return path

def set_save_folder(path: str):
    cfg = _load_config()
    cfg["save_folder"] = path
    _save_config(cfg)
