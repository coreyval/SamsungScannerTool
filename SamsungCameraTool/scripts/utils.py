import os, sys, subprocess, time, tkinter as tk
from tkinter import messagebox
from pathlib import Path

import platform
import subprocess

APP_NAME = "Samsung Scanner Tool"

def base_dir() -> str:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.as_posix()
    # scripts/ lives under the app root; go up one from this file
    return Path(__file__).resolve().parent.parent.as_posix()

def tool_path(filename: str) -> str:
    return os.path.join(base_dir(), "tools", filename)

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def info(msg: str, title: str = APP_NAME):
    messagebox.showinfo(title, msg)

def warn(msg: str, title: str = APP_NAME):
    messagebox.showwarning(title, msg)

def error(msg: str, title: str = APP_NAME):
    messagebox.showerror(title, msg)

def run(cmd, check=False, **kwargs):
    # text + capture_output default so we can inspect stdout/stderr
    kw = dict(text=True, capture_output=True)
    kw.update(_hidden_proc_kwargs())
    kw.update(kwargs)
    return subprocess.run(cmd, check=check, **kw)

def run_adb_shell(args):
    adb = tool_path("adb.exe")
    res = run([adb, "shell"] + args)
    return res.stdout.strip(), res.stderr.strip()

def run_adb(args):
    adb = tool_path("adb.exe")
    return run([adb] + args)

def _hidden_proc_kwargs():
    """Return kwargs to hide console windows on Windows."""
    if platform.system() == "Windows":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return {"startupinfo": si, "creationflags": subprocess.CREATE_NO_WINDOW}
    return {}

CAMERA_DIR = "/sdcard/DCIM/Camera"

def list_device_photos() -> list[str]:
    r = subprocess.run(
        [tool_path("adb.exe"), "shell", "ls", "-1", CAMERA_DIR],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return []  # treat as empty if folder missing
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]

def pull_device_file(remote_name: str, dest_folder: str):
    ensure_dir(dest_folder)
    adb = tool_path("adb.exe")
    remote = f"/sdcard/DCIM/Camera/{remote_name}"
    # quiet pull
    return subprocess.run([adb, "pull", remote, os.path.join(dest_folder, remote_name)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def delete_all_on_device() -> str | None:
    files = list_device_photos()
    if not files:
        return None
    for fn in files:
        subprocess.run(
            [tool_path("adb.exe"), "shell", "rm", "-f", f"{CAMERA_DIR}/{fn}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    return None

