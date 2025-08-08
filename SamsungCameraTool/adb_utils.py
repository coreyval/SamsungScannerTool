import os
import subprocess
from typing import List
from file_utils import tool_path, ensure_folder_exists

ADB = lambda *args: [tool_path("adb.exe"), *args]  # windows-bundled adb
SCRCPY = lambda *args: [tool_path("scrcpy.exe"), *args]

def _run(cmd: list, check: bool = False, text: bool = True):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text, check=check)

def start_scrcpy():
    exe = tool_path("scrcpy.exe")
    if not os.path.exists(exe):
        raise FileNotFoundError("scrcpy.exe not found in tools/")
    # Non-blocking
    subprocess.Popen(SCRCPY("--stay-awake"),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def connect_wirelessly() -> str:
    # Get device IP
    res = _run(ADB("shell", "ip", "route"))
    if res.returncode != 0 or "src" not in res.stdout:
        raise RuntimeError(res.stderr or "Unable to obtain phone IP.")
    ip_address = res.stdout.split("src")[-1].strip().split()[0]

    # Enable tcpip and connect
    _run(ADB("tcpip", "5555"), check=True)
    _run(ADB("connect", ip_address), check=True)
    return ip_address

def launch_camera_app():
    _run(ADB("shell", "am", "start", "-n", "com.sec.android.app.camera/.Camera"), check=True)

def trigger_camera():
    _run(ADB("shell", "input", "keyevent", "27"), check=True)  # KEYCODE_CAMERA

def list_photos() -> List[str]:
    res = _run(ADB("shell", "ls", "-t", "/sdcard/DCIM/Camera"))
    if res.returncode != 0:
        return []
    names = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    # Filter only common image/video extensions, optional:
    return [n for n in names if any(n.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".heic", ".mp4", ".mov"))]

def pull_file(remote_name: str, local_dir: str) -> str:
    ensure_folder_exists(local_dir)
    local_path = os.path.join(local_dir, remote_name)
    _run(ADB("pull", f"/sdcard/DCIM/Camera/{remote_name}", local_path))
    return local_path

def pull_all_photos_to(local_dir: str) -> List[str]:
    ensure_folder_exists(local_dir)
    names = list_photos()
    pulled = []
    for n in names:
        local_path = os.path.join(local_dir, n)
        if not os.path.exists(local_path):
            _run(ADB("pull", f"/sdcard/DCIM/Camera/{n}", local_path))
        if os.path.exists(local_path):
            pulled.append(local_path)
    return pulled

def delete_all_photos_on_phone() -> str:
    # Use -f to ignore missing; quote path
    res = _run(ADB("shell", "rm", "-f", "/sdcard/DCIM/Camera/*"))
    if res.returncode != 0 and res.stderr:
        raise RuntimeError(res.stderr)
    return res.stdout.strip() or "OK"
