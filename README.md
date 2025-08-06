# Samsung Camera Tool 📸

A simple and user-friendly image viewer and export tool designed to preview, manage, and export photos captured from a connected Samsung device.

## ✨ Features

- 🔍 Image Carousel: Browse images one-by-one with `Prev` and `Next` buttons  
- 🗑️ Delete: Remove unwanted photos directly from the interface  
- ✅ Select: Choose specific images for batch export  
- 🔢 Jump to Image: Go to a specific photo by index  
- 📂 Export Options:  
  - Export Selected: Copy only selected images to a folder  
  - Export All: Copy all images at once

## 🛠 Requirements

- Python 3.7+  
- Dependencies:  
  - tkinter  
  - Pillow  
  - shutil  
  - os  

Install required libraries:  
```bash
pip install pillow
```

## 🚀 Usage

Run the script:
```bash
python main.py
```

Use the interface to view, delete, and export images.

## 📁 Folder Structure

- All images should be placed inside the `captures/` folder by default  
- Export directories can be chosen during use

## 💡 Notes

- Image orientation is automatically adjusted  
- Deleted images are permanently removed, so proceed with caution  
- This tool is ideal for reviewing and exporting batches of mobile-captured images quickly

## 📷 Command to Build
The program will not work without the following libraries installed. Make sure these are installed and Python is in your path.
pip install Pillow
pip install opencv-python
pip install Pyinstaller

Use this command within the folder.
pyinstaller --noconsole --onefile --add-data "tools;tools" --add-data "captures;captures" --name "Samsung Scanner Tool" main.py
