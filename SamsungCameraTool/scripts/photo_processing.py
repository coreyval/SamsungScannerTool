# scripts/photo_processing.py !

import os
import tkinter as tk
from tkinter import messagebox, simpledialog

from .photo_viewer import view_phone_photos
from .utils import (
    info, warn, error, ensure_dir,
    list_device_photos, pull_device_file, delete_all_on_device,
)

def prompt_asset_tag() -> str | None:
    return simpledialog.askstring("Process Phone", "Scan or enter asset tag:")

def _choice_dialog(parent: tk.Misc) -> str | None:
    """
    Modal with three choices:
      - 'finish'
      - 'view'
      - 'more'
    Returns one of those strings, or None if closed.
    """
    result = {"val": None}
    win = tk.Toplevel(parent)
    win.title("Next Step")
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()

    tk.Label(
        win,
        text="When you're ready, choose an option:",
        padx=12, pady=10, justify="left",
    ).pack(anchor="w")

    btns = tk.Frame(win)
    btns.pack(padx=10, pady=10)

    def _set(v: str):
        result["val"] = v
        win.destroy()

    tk.Button(btns, text="✅ Finish processing", width=20, command=lambda: _set("finish")).grid(row=0, column=0, padx=6, pady=4)
    tk.Button(btns, text="👁️ View photos",      width=20, command=lambda: _set("view")).grid(  row=0, column=1, padx=6, pady=4)
    tk.Button(btns, text="➕ Add more photos",   width=20, command=lambda: _set("more")).grid(  row=0, column=2, padx=6, pady=4)

    # Center on parent using the child's requested size
    parent.update_idletasks()
    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width()  - win.winfo_width())  // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

    parent.wait_window(win)
    return result["val"]

# scripts/photo_processing.py

import os
import tkinter as tk
from tkinter import messagebox, simpledialog

from .photo_viewer import view_phone_photos
from .utils import (
    info, warn, error, ensure_dir,
    list_device_photos, pull_device_file, delete_all_on_device,
)

def prompt_asset_tag() -> str | None:
    return simpledialog.askstring("Process Phone", "Scan or enter asset tag:")

def _choice_dialog(parent: tk.Misc) -> str | None:
    """
    Modal with three choices:
      - 'finish'
      - 'view'
      - 'more'
    Returns one of those strings, or None if closed.
    """
    result = {"val": None}
    win = tk.Toplevel(parent)
    win.title("Next Step")
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()

    tk.Label(
        win,
        text="When you're ready, choose an option:",
        padx=12, pady=10, justify="left",
    ).pack(anchor="w")

    btns = tk.Frame(win)
    btns.pack(padx=10, pady=10)

    def _set(v: str):
        result["val"] = v
        win.destroy()

    tk.Button(btns, text="✅ Finish processing", width=20, command=lambda: _set("finish")).grid(row=0, column=0, padx=6, pady=4)
    tk.Button(btns, text="👁️ View photos",      width=20, command=lambda: _set("view")).grid(  row=0, column=1, padx=6, pady=4)
    tk.Button(btns, text="➕ Add more photos",   width=20, command=lambda: _set("more")).grid(  row=0, column=2, padx=6, pady=4)

    # Center on parent using the child's requested size
    parent.update_idletasks()
    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width()  - win.winfo_width())  // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{x}+{y}")

    parent.wait_window(win)
    return result["val"]


def process_phone(
        save_root: str,
        delete_after: bool = True,
        on_view=None,
        tk_parent: tk.Misc | None = None,
) -> None:
    while True:  # Loop until we have a final tag or cancel
        tag = prompt_asset_tag()
        if not tag:
            return  # Cancelled

        dest = os.path.join(save_root, tag)
        ensure_dir(dest)

        # Check if folder already has files
        if os.path.exists(dest) and os.listdir(dest):
            resp = messagebox.askyesnocancel(
                "Asset Tag Exists",
                f"A folder for asset tag '{tag}' already exists and has files.\n\n"
                "Yes = Add new phone photos to this folder\n"
                "No = Enter a different asset tag\n"
                "Cancel = Stop processing"
            )
            if resp is None:  # Cancel
                return
            if resp is False:  # No → loop to prompt for a new tag
                continue
            # Yes → break out of loop and proceed
        break

    # Initial reminder to take photos
    messagebox.showinfo(
        "Take Photos",
        "Open the camera and take your photos now.\n\n"
        "When you're done, choose an option:\n"
        "• Finish processing\n"
        "• View photos\n"
        "• Add more photos"
    )

    parent = tk_parent or (tk._default_root if tk._default_root else None)
    while True:
        if parent:
            choice = _choice_dialog(parent)
        else:
            yn = messagebox.askyesno(
                "Finish?",
                "Do you want to finish processing now?\n\n"
                "Yes = Finish processing\nNo = Add more photos\n\n"
                "(Use the main menu to view photos)"
            )
            choice = "finish" if yn else "more"

        if choice == "view":
            files_now = list_device_photos() or []
            if not files_now:
                messagebox.showinfo("No Photos", "There are no photos on the phone to view.")
                continue
            if callable(on_view):
                on_view()
            else:
                view_phone_photos(parent)
            continue

        elif choice == "more":
            # Remind user to take more photos, then loop back
            messagebox.showinfo(
                "Add More Photos",
                "Open the camera and take more photos now.\n\n"
                "When you're done, choose an option again."
            )
            continue

        elif choice == "finish":
            break

    # --- Pull & save ---
    files = list_device_photos()
    if not files:
        warn("No photos found on the phone.")
        return

    pulled = 0
    for fn in files:
        pull_device_file(fn, dest)
        pulled += 1

    if delete_after:
        err = delete_all_on_device()
        if err:
            error("Finished saving, but failed to delete from phone:\n" + err)
            return
        info(f"✅ Saved {pulled} file(s) to:\n{dest}\n\n🗑 Phone Camera folder cleared.")
    else:
        info(f"✅ Saved {pulled} file(s) to:\n{dest}\n\n(Phone photos were NOT deleted.)")
