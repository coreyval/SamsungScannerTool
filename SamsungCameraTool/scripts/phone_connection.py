import time
from .utils import run_adb, run_adb_shell, info, error

from pathlib import Path
import os, sys, subprocess

def connect_wirelessly():
    # Must already be USB-connected once & same Wi-Fi
    out, _ = run_adb_shell(["ip", "route"])
    if not out:
        error("Could not read device IP route.\nMake sure the phone is connected via USB and USB debugging is ON.")
        return
    try:
        ip = out.split("src")[-1].strip().split()[0]
    except Exception:
        error("Failed to parse device IP.\nOutput:\n" + out)
        return

    run_adb(["tcpip", "5555"])
    time.sleep(1)
    res = run_adb(["connect", ip])
    if "connected to" in (res.stdout or ""):
        info(f"📡 Connected wirelessly to {ip}")
    else:
        error(f"Failed to connect to {ip}\n\n{res.stdout}\n{res.stderr}")
