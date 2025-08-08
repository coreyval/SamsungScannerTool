import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from config_manager import get_save_folder, set_save_folder, ensure_config_initialized
from file_utils import get_paths, tool_path, ensure_folder_exists
from adb_utils import (
    start_scrcpy, connect_wirelessly, launch_camera_app,
    trigger_camera, list_photos, pull_all_photos_to,
    delete_all_photos_on_phone
)
from photo_viewer import PhotoViewer

# ---------- App bootstrap ----------
BASE_DIR, TOOLS_DIR, CAPTURE_DIR, TEMP_VIEW_DIR = get_paths()
ensure_config_initialized(default_save_dir=CAPTURE_DIR)
ensure_folder_exists(CAPTURE_DIR)
ensure_folder_exists(TEMP_VIEW_DIR)

root = tk.Tk()
root.title("Samsung Camera Tool")
root.geometry("320x520")
root.attributes('-topmost', True)

# ---------- Handlers ----------
def on_quit():
    if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
        # Best-effort kill scrcpy, ignore if not running
        try:
            import subprocess
            subprocess.run(["taskkill", "/f", "/im", "scrcpy.exe"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        root.destroy()
        sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_quit)

def do_connect_wirelessly():
    try:
        ip = connect_wirelessly()
        messagebox.showinfo("Connected", f"📡 Connected wirelessly to {ip}")
    except Exception as e:
        messagebox.showerror("Wireless Error", f"❌ Failed to connect wirelessly:\n{e}")

def do_open_camera():
    try:
        launch_camera_app()
    except Exception as e:
        messagebox.showerror("Camera Error", f"Failed to open camera:\n{e}")

def do_take_photo():
    try:
        trigger_camera()
        messagebox.showinfo("Captured", "📸 Shutter triggered.")
    except Exception as e:
        messagebox.showerror("Capture Error", f"Failed to capture:\n{e}")

def do_live_view():
    try:
        start_scrcpy()
    except FileNotFoundError:
        messagebox.showerror("scrcpy Not Found", "⚠️ scrcpy.exe is missing in tools/")
    except Exception as e:
        messagebox.showerror("Live View Error", f"{e}")

def do_view_all_photos():
    # Pull everything from phone into temp_view, then open viewer
    def worker():
        try:
            pulled = pull_all_photos_to(TEMP_VIEW_DIR)
            if not pulled:
                messagebox.showinfo("No Photos", "No photos found on the device.")
                return
            # Open viewer on UI thread
            root.after(0, lambda: PhotoViewer(root, pulled))
        except Exception as e:
            messagebox.showerror("Pull Error", f"Failed to pull photos:\n{e}")
    threading.Thread(target=worker, daemon=True).start()

def do_set_save_folder():
    folder = filedialog.askdirectory(title="Select Save Folder")
    if not folder:
        return
    ensure_folder_exists(folder)
    set_save_folder(folder)
    messagebox.showinfo("Set", f"Save folder set to:\n{folder}")

def do_download_all_photos():
    save_dir = get_save_folder()
    if not save_dir:
        messagebox.showerror("No Folder", "Please set a save folder first.")
        return

    def worker():
        try:
            pulled = pull_all_photos_to(save_dir)
            msg = f"{len(pulled)} photo(s) downloaded to:\n{save_dir}"
            root.after(0, lambda: messagebox.showinfo("Download Complete", msg))
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"Failed to download:\n{e}"))

    threading.Thread(target=worker, daemon=True).start()

def do_delete_all_photos_on_phone():
    if not messagebox.askyesno(
        "Delete All",
        "⚠ This will permanently delete ALL photos from the phone's Camera folder. Continue?"
    ):
        return
    try:
        deleted = delete_all_photos_on_phone()
        messagebox.showinfo("Deleted", f"All photos deleted from phone.\n{deleted}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete all photos:\n{e}")

# ---------- UI ----------
button_frame = tk.Frame(root)
button_frame.pack(expand=True, pady=8)

buttons = [
    ("📶 Connect Wirelessly", do_connect_wirelessly),
    ("📱 Open Camera App",    do_open_camera),
    ("📸 Take Photo",         do_take_photo),
    ("👁️ Live View",         do_live_view),
    ("🖼 View All Phone Photos", do_view_all_photos),
    ("📂 Set Save Folder",    do_set_save_folder),
    ("📥 Download All Photos",do_download_all_photos),
    ("🗑 Delete All on Phone",do_delete_all_photos_on_phone),
    ("❎ Quit App",           on_quit),
]

for i, (label, func) in enumerate(buttons):
    row, col = divmod(i, 2)
    btn = tk.Button(button_frame, text=label, command=func, height=2, width=18)
    btn.grid(row=row, column=col, padx=6, pady=6)

root.mainloop()
