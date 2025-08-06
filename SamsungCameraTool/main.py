import os
import sys
import time
import subprocess
from datetime import datetime
from PIL import Image, ExifTags, ImageTk
import cv2
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, Button, Frame, LEFT
import numpy as np
import threading
import shutil


# ---------- Directory Setup ----------
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = resource_path("tools")
CAPTURE_DIR = resource_path("captures")
TEMP_VIEW_DIR = os.path.join(CAPTURE_DIR, "temp_view")

os.makedirs(CAPTURE_DIR, exist_ok=True)
os.makedirs(TEMP_VIEW_DIR, exist_ok=True)
SAVE_DIR = CAPTURE_DIR


# Ensure folders exist
os.makedirs(CAPTURE_DIR, exist_ok=True)
os.makedirs(TEMP_VIEW_DIR, exist_ok=True)

# Default save directory
SAVE_DIR = CAPTURE_DIR

# ---------- GUI Root ----------
root = tk.Tk()
root.title("Samsung Camera Tool")
root.geometry("300x500")
root.attributes('-topmost', True)

# ---------- Helper Tips ----------
def show_help():
    help_text = (
        "📸 Welcome to Samsung Camera Tool!\n\n"
        "• Connect Wirelessly:\n"
        "  Plug in your phone via USB to enable wireless control.\n\n"
        "• Open Camera App:\n"
        "  Launches the default camera app on your phone.\n\n"
        "• Take Photo:\n"
        "  Captures a photo remotely using your phone.\n\n"
        "• Live View:\n"
        "  Opens scrcpy for viewing and controlling your phone screen.\n\n"
        "• View All Phone Photos:\n"
        "  Pulls all recent photos from your phone for preview.\n\n"
        "• Set Save Folder:\n"
        "  Choose where the captured images are saved on your PC.\n\n"
        "• Quit App:\n"
        "  Closes this program.\n\n"
        "💾 Default save folder: 'captures'"
    )
    messagebox.showinfo("User Guide", help_text)


# ---------- Quit ----------
def quit_app():
    if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
        try:
            subprocess.run(["taskkill", "/f", "/im", "scrcpy.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"⚠️ Could not kill scrcpy: {e}")
        root.destroy()
        sys.exit(0)
root.protocol("WM_DELETE_WINDOW", quit_app)

# ---------- SCRCPY ----------
def tool_path(filename):
    return os.path.join(TOOLS_DIR, filename)

def start_standard_view():
    try:
        process = subprocess.Popen(
            [tool_path("scrcpy.exe"), "--stay-awake"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Let it run for a short time, then check output
        time.sleep(2)
        stdout, stderr = process.communicate(timeout=5)

        # Check for common scrcpy errors
        if "state=offline" in stderr or "Device disconnected" in stderr or "Server connection failed" in stderr:
            messagebox.showerror("Live View Error", "❌ scrcpy failed to connect.\nMake sure your phone is online and connected via ADB.")
        elif process.returncode is not None and process.returncode != 0:
            messagebox.showerror("Live View Error", f"❌ scrcpy exited with error code {process.returncode}.")
    except subprocess.TimeoutExpired:
        messagebox.showerror("Timeout", "scrcpy took too long to respond.")
    except FileNotFoundError:
        messagebox.showerror("scrcpy Not Found", "⚠️ scrcpy.exe is missing.\nPlease reinstall the tool.")
    except Exception as e:
        messagebox.showerror("Unknown Error", f"An unexpected error occurred:\n{str(e)}")


# ---------- ADB ----------
def run_adb(cmd):
    result = subprocess.run([tool_path("adb.exe"), "shell"] + cmd, capture_output=True, text=True)
    if "device offline" in result.stderr.lower():
        messagebox.showerror("ADB Error", "❌ ADB reports your device is offline.\n\nTry:\n- Reconnecting USB\n- Accepting the debugging prompt on your phone\n- Running `adb kill-server` and `adb start-server`")
        return ""
    return result.stdout.strip()


def list_photos():
    output = run_adb(["ls", "-t", "/sdcard/DCIM/Camera"])
    return output.splitlines()

def pull_photo(file_name, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, file_name)
    subprocess.run([tool_path("adb.exe"), "pull", f"/sdcard/DCIM/Camera/{file_name}", local_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return local_path

def launch_camera_app():
    try:
        subprocess.run([tool_path("adb.exe"), "shell", "am", "start", "-n", "com.sec.android.app.camera/.Camera"])
    except Exception as e:
        messagebox.showerror("Camera Error", f"Failed to open camera: {e}")

def trigger_camera():
    try:
        subprocess.run([tool_path("adb.exe"), "shell", "input", "keyevent", "27"])
    except Exception as e:
        messagebox.showerror("Capture Error", f"Failed to capture photo: {e}")

def pull_all_photos():
    photos = list_photos()
    if not photos:
        messagebox.showinfo("No Photos", "No photos found on the device.")
        return []

    for file in photos:
        pull_photo(file, TEMP_VIEW_DIR)
    return [os.path.join(TEMP_VIEW_DIR, f) for f in photos if os.path.exists(os.path.join(TEMP_VIEW_DIR, f))]

# ---------- Image Viewer ----------
def preview_carousel(image_paths):
    if not image_paths:
        return

    win = tk.Toplevel()
    win.title("Photo Viewer")

    current = [0]  # Use list for mutability
    selected = set()
    images = []  # <-- Store PhotoImage references here

    img_label = tk.Label(win)
    img_label.pack()

    def show_image(index):
        img_path = image_paths[index]
        try:
            img = load_image_auto_orient(img_path)
            img.thumbnail((500, 500))
            photo = ImageTk.PhotoImage(img)
            img_label.configure(image=photo)
            img_label.image = photo  # <-- Prevent garbage collection
            images.append(photo)     # <-- Keep global reference
        except Exception as e:
            messagebox.showerror("Image Error", f"❌ Failed to load image: {e}")

    def next_image():
        if current[0] < len(image_paths) - 1:
            current[0] += 1
            show_image(current[0])

    def prev_image():
        if current[0] > 0:
            current[0] -= 1
            show_image(current[0])

    def delete_image():
        idx = current[0]
        try:
            os.remove(image_paths[idx])
            del image_paths[idx]
            if idx >= len(image_paths):
                current[0] = max(0, len(image_paths) - 1)
            show_image(current[0]) if image_paths else win.destroy()
        except Exception as e:
            messagebox.showerror("Delete Error", f"❌ Failed to delete: {e}")

    def toggle_select():
        idx = current[0]
        if idx in selected:
            selected.remove(idx)
        else:
            selected.add(idx)

    def go_to_number():
        try:
            idx = int(simpledialog.askstring("Go to", f"Enter image index (0 - {len(image_paths)-1})"))
            if 0 <= idx < len(image_paths):
                current[0] = idx
                show_image(current[0])
        except:
            pass

    def export_selected():
        if not selected:
            messagebox.showinfo("None Selected", "No images selected.")
            return
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if export_dir:
            for idx in selected:
                src = image_paths[idx]
                dst = os.path.join(export_dir, os.path.basename(src))
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export {src}:\n{e}")
            messagebox.showinfo("Done", f"Exported {len(selected)} files.")

    def export_all():
        export_dir = filedialog.askdirectory(title="Export All Images To...")
        if export_dir:
            for path in image_paths:
                try:
                    shutil.copy2(path, os.path.join(export_dir, os.path.basename(path)))
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export {path}:\n{e}")
            messagebox.showinfo("Done", f"Exported {len(image_paths)} files.")

    # Buttons
    buttons = [
        ("◀ Prev", prev_image),
        ("▶ Next", next_image),
        ("🗑 Delete", delete_image),
        ("✅ Select", toggle_select),
        ("# Go to #", go_to_number),
        ("📤 Export Selected", export_selected),
        ("📦 Export All", export_all)
    ]

    # Row 1: Prev / Next
    row1 = Frame(win)
    row1.pack(pady=2)
    Button(row1, text='⬅ Prev', command=prev_image).pack(side=LEFT, padx=2)
    Button(row1, text='➡ Next', command=next_image).pack(side=LEFT, padx=2)

    # Row 2: Delete / Select
    row2 = Frame(win)
    row2.pack(pady=2)
    Button(row2, text='🗑 Delete', command=delete_image).pack(side=LEFT, padx=2)
    Button(row2, text='✅ Select', command=toggle_select).pack(side=LEFT, padx=2)

    # Row 3: Go to # / Export Selected / Export All
    row3 = Frame(win)
    row3.pack(pady=2)
    Button(row3, text='# Go to #', command=go_to_number).pack(side=LEFT, padx=2)
    Button(row3, text='📂 Export Selected', command=export_selected).pack(side=LEFT, padx=2)
    Button(row3, text='📦 Export All', command=export_all).pack(side=LEFT, padx=2)

    # 👉 Show first image on load
    show_image(current[0])

def load_image_auto_orient(path):
    img = Image.open(path)

    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = img._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation, None)

            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)
    except Exception as e:
        print(f"EXIF auto-rotate failed: {e}")

    return img

# ---------- Handlers ----------
def take_photo():
    trigger_camera()
    time.sleep(0.5)
    photos = list_photos()
    if photos:
        path = pull_photo(photos[0], SAVE_DIR)
        messagebox.showinfo("Saved", f"Photo saved to: {path}")

def set_save_dir():
    global SAVE_DIR
    folder = filedialog.askdirectory(title="Select Save Folder")
    if folder:
        SAVE_DIR = folder
        os.makedirs(SAVE_DIR, exist_ok=True)
        messagebox.showinfo("Set", f"Save folder set to: {SAVE_DIR}")

def view_all_photos():
    threading.Thread(target=lambda: preview_carousel(pull_all_photos())).start()

def connect_wirelessly():
    confirm = messagebox.askyesno(
        "USB Connection Required",
        "⚠️ Your phone must be plugged in via USB first to enable wireless ADB and connected to the same network.\n\nContinue?"
    )
    if not confirm:
        return

    try:
        ip_output = subprocess.check_output([tool_path("adb.exe"), "shell", "ip", "route"], text=True)
        ip_address = ip_output.split("src")[-1].strip().split()[0]

        subprocess.run([tool_path("adb.exe"), "tcpip", "5555"], check=True)
        time.sleep(1)

        subprocess.run([tool_path("adb.exe"), "connect", ip_address], check=True)
        messagebox.showinfo("Connected", f"📡 Connected wirelessly to {ip_address}")
    except Exception as e:
        messagebox.showerror("Wireless Error", f"❌ Failed to connect wirelessly:\n{e}")

# ---------- GUI Setup ----------
button_frame = tk.Frame(root)
button_frame.pack(expand=True)

buttons = [
    ("📶 Connect Wirelessly", connect_wirelessly),
    ("📱 Open Camera App", launch_camera_app),
    ("📸 Take Photo", take_photo),
    ("👁️ Live View", start_standard_view),
    ("🖼 View All Phone Photos", view_all_photos),
    ("📂 Set Save Folder", set_save_dir),
    ("❓ Help", show_help),
    ("❎ Quit App", quit_app),
]

for i, (label, func) in enumerate(buttons):
    row = i // 2
    col = i % 2
    btn = tk.Button(button_frame, text=label, command=func, height=2, width=16)
    btn.grid(row=row, column=col, padx=5, pady=5)

root.mainloop()

# Corey