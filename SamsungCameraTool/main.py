import tkinter as tk
from tkinter import filedialog
from scripts.config_manager import load_config, save_config
from scripts.phone_connection import connect_wirelessly
from scripts.live_view import start_live_view
from scripts.photo_processing import process_phone
from scripts.utils import ensure_dir, info

# --- App state/config ---
cfg = load_config()
SAVE_DIR = cfg["save_dir"]
ensure_dir(SAVE_DIR)

# --- GUI ---
root = tk.Tk()
root.title("Samsung Scanner Tool")
root.geometry("250x250")
root.attributes("-topmost", True)

def set_save_folder():
    global SAVE_DIR, cfg
    folder = filedialog.askdirectory(title="Choose Save Folder", initialdir=SAVE_DIR)
    if not folder:
        return
    SAVE_DIR = folder
    ensure_dir(SAVE_DIR)
    cfg["save_dir"] = SAVE_DIR
    save_config(cfg)
    info(f"Save folder set to:\n{SAVE_DIR}")

# Buttons (only four)
btns = [
    ("📷 Process Photos", lambda: process_phone(SAVE_DIR, delete_after=True)),
    ("📶 Connect Wirelessly", connect_wirelessly),
    ("👁️ Live View", start_live_view),
    ("📂 Set Save Folder", set_save_folder),
]

wrap = tk.Frame(root); wrap.pack(expand=True, pady=12)
for text, fn in btns:
    tk.Button(wrap, text=text, command=fn, width=26, height=2).pack(pady=6)

root.mainloop()