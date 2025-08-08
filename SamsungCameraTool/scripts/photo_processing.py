import os
from tkinter import simpledialog
from .utils import (
    info, warn, error, ensure_dir,
    list_device_photos, pull_device_file, delete_all_on_device,
)

def prompt_asset_tag() -> str | None:
    return simpledialog.askstring("Process Phone", "Scan or enter asset tag:")

def process_phone(save_root: str, delete_after: bool = True):
    # 1) Ask for asset tag
    tag = prompt_asset_tag()
    if not tag:
        return
    dest = os.path.join(save_root, tag)
    ensure_dir(dest)

    # 2) Pull all photos
    files = list_device_photos()
    if not files:
        warn("No photos found on phone.")
        return

    pulled = 0
    for fn in files:
        pull_device_file(fn, dest)
        pulled += 1

    # 3) Optionally delete from the phone
    if delete_after:
        err = delete_all_on_device()
        if err:
            error("Finished saving, but failed to delete from phone:\n" + err)
            return
        info(f"✅ Saved {pulled} file(s) to:\n{dest}\n\n🗑 Phone Camera folder cleared.")
    else:
        info(f"✅ Saved {pulled} file(s) to:\n{dest}\n\n(Phone photos were NOT deleted.)")
