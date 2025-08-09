import time, re
from .utils import run_adb, run_adb_shell, info, error

CURRENT_DEVICE = None

def _shell_s(args):
    """
    Run: adb -s <device> shell <args...>
    Returns (stdout, stderr) as strings.
    """
    if not CURRENT_DEVICE:
        return "", "no device"
    # run_adb returns CompletedProcess; we need to build the full argv
    cp = run_adb(["-s", CURRENT_DEVICE, "shell"] + (args if isinstance(args, list) else [args]))
    return (cp.stdout or ""), (cp.stderr or "")

def _getprop(key: str) -> str:
    out, _ = _shell_s(["getprop", key])
    return (out or "").strip()

def _battery_summary() -> tuple[str, str]:
    out, _ = _shell_s(["dumpsys", "battery"])
    lvl = re.search(r"\blevel:\s*(\d+)", out or "")
    status = re.search(r"\bstatus:\s*(\d+)", out or "")
    status_map = {"1": "Unknown", "2": "Charging", "3": "Discharging", "4": "Not charging", "5": "Full"}
    return (lvl.group(1) if lvl else "—", status_map.get(status.group(1), "—") if status else "—")

def _storage_summary() -> tuple[str, str]:
    # Human-readable df on internal storage mount
    out, _ = _shell_s(["df", "-h", "/storage/emulated"])
    line = next((ln for ln in (out or "").splitlines() if "/storage/emulated" in ln), "")
    parts = line.split()
    # expected: Filesystem  Size  Used  Avail  Use%  Mounted on
    used = parts[2] if len(parts) > 2 else "—"
    avail = parts[3] if len(parts) > 3 else "—"
    return used, avail

def _device_summary_text() -> str:
    brand = _getprop("ro.product.brand") or "—"
    model = _getprop("ro.product.model") or _getprop("ro.product.name") or "—"
    sdk   = _getprop("ro.build.version.sdk") or "—"
    patch = _getprop("ro.build.version.security_patch") or "—"
    bat, bstat = _battery_summary()
    used, free = _storage_summary()
    lines = [
        f"🔌 Connected to {CURRENT_DEVICE}",
        f"📱 {brand} {model}",
        f"🟢 Android SDK {sdk} (Patch {patch})",
        f"🔋 Battery: {bat}% ({bstat})",
        f"💾 Storage: {used} used, {free} free",
    ]
    return "\n".join(lines)

def connect_wirelessly():
    """
    Requires one-time USB pairing & same Wi-Fi network.
    """
    # Discover IP from route on the phone (via USB ADB)
    out, _ = run_adb_shell(["ip", "route"])
    if not out:
        error("Could not read device IP route.\nMake sure the phone is connected via USB and USB debugging is ON.")
        return
    try:
        ip = out.split("src")[-1].strip().split()[0]
    except Exception:
        error("Failed to parse device IP.\nOutput:\n" + out)
        return

    # Switch to TCP/IP and connect
    run_adb(["tcpip", "5555"])
    time.sleep(1)
    res = run_adb(["connect", ip])  # your run_adb returns CompletedProcess
    ok_text = ((res.stdout or "") + (res.stderr or "")).lower()
    if "connected to" in ok_text or "already connected to" in ok_text:
        # Store explicit target with port so subsequent shell calls hit this device
        global CURRENT_DEVICE
        CURRENT_DEVICE = f"{ip}:5555"
        info(_device_summary_text())
    else:
        error(f"Failed to connect to {ip}\n\n{res.stdout}\n{res.stderr}")
