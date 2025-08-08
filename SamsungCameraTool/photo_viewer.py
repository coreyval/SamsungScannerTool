import os
import shutil
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk, ExifTags

def _auto_orient(img: Image.Image) -> Image.Image:
    try:
        exif = img._getexif()
        if not exif:
            return img
        orientation_key = next((k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None)
        if not orientation_key:
            return img
        o = exif.get(orientation_key)
        if o == 3:
            img = img.rotate(180, expand=True)
        elif o == 6:
            img = img.rotate(270, expand=True)
        elif o == 8:
            img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img

class PhotoViewer(tk.Toplevel):
    def __init__(self, master, image_paths):
        super().__init__(master)
        self.title("Photo Viewer")
        self.images = list(image_paths)  # local copy
        self.idx = 0
        self.selected = set()
        self._tk_cache = []

        self.panel = tk.Label(self)
        self.panel.pack()

        self.label = tk.Label(self, text="", pady=5)
        self.label.pack()

        rows = []
        for _ in range(3):
            row = tk.Frame(self)
            row.pack(pady=2)
            rows.append(row)

        tk.Button(rows[0], text='⬅ Prev', command=self.prev_img).pack(side=tk.LEFT, padx=2)
        tk.Button(rows[0], text='➡ Next', command=self.next_img).pack(side=tk.LEFT, padx=2)

        tk.Button(rows[1], text='🗑 Delete (PC copy)', command=self.delete_local).pack(side=tk.LEFT, padx=2)
        tk.Button(rows[1], text='✅ Select', command=self.toggle_select).pack(side=tk.LEFT, padx=2)

        tk.Button(rows[2], text='# Go to #', command=self.go_to_index).pack(side=tk.LEFT, padx=2)
        tk.Button(rows[2], text='📂 Export Selected', command=self.export_selected).pack(side=tk.LEFT, padx=2)
        tk.Button(rows[2], text='📦 Export All', command=self.export_all).pack(side=tk.LEFT, padx=2)

        self.show_image()  # show first

    def show_image(self):
        if not self.images:
            messagebox.showinfo("No Photos", "No more photos.")
            self.destroy()
            return
        path = self.images[self.idx]
        try:
            img = Image.open(path)
            img = _auto_orient(img)
            img.thumbnail((600, 600))
            tk_img = ImageTk.PhotoImage(img)
            self.panel.configure(image=tk_img)
            self.panel.image = tk_img
            self._tk_cache.append(tk_img)  # prevent GC
            self.label.configure(text=f"{self.idx+1}/{len(self.images)} • {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Image Error", f"❌ Failed to load image:\n{e}")

    def next_img(self):
        if self.idx < len(self.images) - 1:
            self.idx += 1
            self.show_image()

    def prev_img(self):
        if self.idx > 0:
            self.idx -= 1
            self.show_image()

    def delete_local(self):
        path = self.images[self.idx]
        try:
            if os.path.exists(path):
                os.remove(path)
            del self.images[self.idx]
            if self.idx >= len(self.images):
                self.idx = max(0, len(self.images) - 1)
            self.show_image() if self.images else self.destroy()
        except Exception as e:
            messagebox.showerror("Delete Error", f"❌ Failed to delete:\n{e}")

    def toggle_select(self):
        if self.idx in self.selected:
            self.selected.remove(self.idx)
        else:
            self.selected.add(self.idx)

    def go_to_index(self):
        try:
            value = int(simpledialog.askstring("Go to", f"Enter photo number (1-{len(self.images)}):"))
            if 1 <= value <= len(self.images):
                self.idx = value - 1
                self.show_image()
        except Exception:
            pass

    def export_selected(self):
        if not self.selected:
            messagebox.showinfo("None Selected", "No images selected.")
            return
        folder = filedialog.askdirectory(title="Export Selected To...")
        if not folder:
            return
        count = 0
        for i in list(self.selected):
            src = self.images[i]
            dst = os.path.join(folder, os.path.basename(src))
            try:
                shutil.copy2(src, dst)
                count += 1
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export {src}:\n{e}")
        messagebox.showinfo("Export Complete", f"Exported {count} file(s).")

    def export_all(self):
        folder = filedialog.askdirectory(title="Export All To...")
        if not folder:
            return
        count = 0
        for src in self.images:
            dst = os.path.join(folder, os.path.basename(src))
            try:
                shutil.copy2(src, dst)
                count += 1
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export {src}:\n{e}")
        messagebox.showinfo("Export Complete", f"Exported {count} file(s).")
