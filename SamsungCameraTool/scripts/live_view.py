import subprocess
from .utils import tool_path, error, _hidden_proc_kwargs

def start_live_view():
    try:
        subprocess.Popen([tool_path("scrcpy.exe"), "--stay-awake"])
    except FileNotFoundError:
        error("scrcpy.exe not found in tools folder.")
        # done.