# scripts/photo_viewer.py
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps

from .utils import (
    ensure_dir,
    list_device_photos,
    run_adb_shell,        # for per-file delete
    pull_device_file,     # pull to local temp
)

def _camera_path(name: str) -> str:
    # Adjust if your device path differs
    return f"/sdcard/DCIM/Camera/{name}"

def _delete_remote(name: str) -> str | None:
    """Delete a single file from the phone. Returns error text or None on success."""
    out, err = run_adb_shell(["rm", "-f", _camera_path(name)])
    # adb returns nothing on success; if there's stderr or a non-empty stdout, show it
    if err and err.strip():
        return err.strip()
    return None

def view_phone_photos(parent: tk.Tk | tk.Toplevel | None = None, temp_dir: str | None = None):
    """
    Pull current photos from the phone to a temp dir and display a simple viewer.
    Users can select some and delete them from the phone.

    parent: optional Tk parent
    temp_dir: where to cache pulled images (default: captures/temp_view)
    """
    # resolve temp dir
    base = os.path.abspath(os.path.join(os.getcwd(), "captures"))
    temp_dir = temp_dir or os.path.join(base, "temp_view")
    ensure_dir(temp_dir)

    # state
    remote_names: list[str] = []     # filenames on device
    local_paths: list[str] = []      # matching local temp copies
    idx = 0
    selected: set[int] = set()

    def pull_latest():
        nonlocal remote_names, local_paths, idx, selected
        selected.clear()
        remote_names = list_device_photos() or []
        local_paths = []
        if not remote_names:
            messagebox.showinfo("Photos", "No photos found on the phone.")
            return
        for name in remote_names:
            # pull each into temp_dir (skips if exists)
            pull_device_file(name, temp_dir)
            local_paths.append(os.path.join(temp_dir, name))
        idx = 0
        show_current()

    def show_current():
        if not local_paths:
            panel.config(image="", text="No images", compound="center")
            label.configure(text="")
            return
        i = max(0, min(idx, len(local_paths) - 1))
        path = local_paths[i]
        try:
            img = Image.open(path)
            # Auto-rotate based on EXIF Orientation if present
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            img.thumbnail((640, 640), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(img)
            panel.config(image=imgtk, compound=None)
            panel.image = imgtk  # keep ref
        except Exception:
            panel.config(image="", text="(failed to load image)", compound="center")
            panel.image = None
        label.configure(
            text=f"{i+1}/{len(local_paths)}  "
                 f"{os.path.basename(path)}  "
                 f"{'[SELECTED]' if i in selected else ''}"
        )

    def prev_img():
        nonlocal idx
        if not local_paths: return
        idx = (idx - 1) % len(local_paths)
        show_current()

    def next_img():
        nonlocal idx
        if not local_paths: return
        idx = (idx + 1) % len(local_paths)
        show_current()

    def toggle_select():
        if not local_paths: return
        if idx in selected:
            selected.remove(idx)
        else:
            selected.add(idx)
        show_current()

    def delete_selected():
        if not selected:
            messagebox.showinfo("Delete", "No photos selected.")
            return
        confirm = messagebox.askyesno(
            "Delete from phone",
            f"Delete {len(selected)} selected photo(s) from the phone?\n\n"
            "This cannot be undone."
        )
        if not confirm:
            return
        # delete on device by remote name
        errors = []
        # work off a snapshot since we'll mutate lists
        to_delete = sorted(list(selected), reverse=True)
        for i in to_delete:
            name = remote_names[i]
            err = _delete_remote(name)
            if err:
                errors.append(f"{name}: {err}")
            else:
                # remove from local state, best-effort remove temp file
                try:
                    os.remove(local_paths[i])
                except Exception:
                    pass
                del remote_names[i]
                del local_paths[i]
        selected.clear()
        # fix idx
        nonlocal idx
        idx = min(idx, max(0, len(local_paths)-1))
        show_current()
        if errors:
            messagebox.showerror("Some failed", "Failed to delete:\n\n" + "\n".join(errors))
        else:
            messagebox.showinfo("Deleted", "Selected photos removed from phone.")

    # UI
    win = tk.Toplevel(parent) if parent else tk.Toplevel()
    win.title("Phone Photos")
    win.resizable(False, False)

    panel = tk.Label(win, width=640, height=640, bg="#f4f4f4")
    panel.pack(padx=8, pady=(8, 4))

    label = tk.Label(win, text="", anchor="w")
    label.pack(padx=8, pady=(0, 6), fill="x")

    row = tk.Frame(win)
    row.pack(padx=8, pady=6)

    tk.Button(row, text="◀ Prev", width=10, command=prev_img).grid(row=0, column=0, padx=3)
    tk.Button(row, text="Next ▶", width=10, command=next_img).grid(row=0, column=1, padx=3)
    tk.Button(row, text="✅ Select / Unselect", width=18, command=toggle_select).grid(row=0, column=2, padx=6)
    tk.Button(row, text="🗑 Delete Selected (phone)", width=22, command=delete_selected).grid(row=0, column=3, padx=6)
    tk.Button(row, text="↻ Refresh", width=10, command=pull_latest).grid(row=0, column=4, padx=3)
    tk.Button(row, text="Close", width=10, command=win.destroy).grid(row=0, column=5, padx=3)

    # initial load
    pull_latest()
    win.grab_set()
    win.focus_set()
    win.wait_window(win)
