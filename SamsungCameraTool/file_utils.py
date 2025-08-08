import os
import sys

def resource_path(relative_path: str) -> str:
    """
    Works for dev and for PyInstaller onefile.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.join(base_dir, "tools")
    captures_dir = os.path.join(base_dir, "captures")
    temp_view_dir = os.path.join(captures_dir, "temp_view")
    return base_dir, tools_dir, captures_dir, temp_view_dir

def ensure_folder_exists(path: str):
    os.makedirs(path, exist_ok=True)

def tool_path(filename: str) -> str:
    _, tools_dir, _, _ = get_paths()
    return os.path.join(tools_dir, filename)
