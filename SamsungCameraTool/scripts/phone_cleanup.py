# scripts/phone_cleanup.py
import subprocess
import shlex

def _shell_quote(p: str) -> str:
    # Safe for adb shell (handles spaces and single quotes)
    return "'" + p.replace("'", "'\"'\"'") + "'"

def list_device_files(adb_path: str, camera_dir: str = "/sdcard/DCIM/Camera") -> list[str]:
    """Return a list of file names (not full paths) in the camera dir."""
    proc = subprocess.run(
        [adb_path, "shell", f"ls -1 {_shell_quote(camera_dir)} 2>/dev/null"],
        capture_output=True, text=True
    )
    out = (proc.stdout or "").strip()
    if not out or "No such file or directory" in out:
        return []
    # Filter out directories just in case
    return [ln for ln in out.splitlines() if ln and "." in ln]

def delete_all_on_device(
    adb_path: str,
    camera_dir: str = "/sdcard/DCIM/Camera",
    also_thumbnails: bool = True,
    rescan_media: bool = True,
) -> tuple[int, int, int]:
    """
    Delete all files in the camera folder (optionally thumbnails).
    Returns (deleted, skipped, errors).
    """
    files = list_device_files(adb_path, camera_dir)
    deleted = 0
    skipped = 0
    errors = 0

    # Delete each file individually (robust across Android shells)
    for name in files:
        full = f"{camera_dir}/{name}"
        proc = subprocess.run([adb_path, "shell", "rm", "-f", full],
                              capture_output=True, text=True)
        if proc.returncode == 0:
            deleted += 1
        else:
            # If rm spat back “No such file”, count as skipped; otherwise error
            if "No such file" in (proc.stderr or "") or "No such file" in (proc.stdout or ""):
                skipped += 1
            else:
                errors += 1

    # Optionally clear the thumbnail cache (Gallery’s hidden cache)
    if also_thumbnails:
        subprocess.run([adb_path, "shell", "rm", "-f", "/sdcard/DCIM/.thumbnails/*"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Optionally trigger a quick media scan so Gallery updates promptly
    if rescan_media:
        subprocess.run(
            [adb_path, "shell", "am", "broadcast",
             "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
             "-d", f"file://{camera_dir}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    return deleted, skipped, errors
