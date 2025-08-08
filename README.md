# Samsung Scanner Tool 📸

A portable, user-friendly tool for scanning, processing, and managing photos directly from a connected Samsung device using **ADB**. Designed for fast workflow automation, asset tagging, and organized exporting.

## ✨ Features

- 📱 **Wireless or USB Device Connection** – Connect to your Samsung device with ADB over USB or Wi-Fi  
- 🖼 **Live View** – View your phone’s camera feed directly from your PC  
- 📸 **Remote Capture** – Take photos from your device via the app interface  
- 🗂 **Automatic Folder Creation** – Organizes photos into folders based on scanned asset tags  
- 📦 **Process Photos** –  
  - Finish processing to move images into the correct tagged folder  
  - Automatically prevents reprocessing of the same asset tag  
- 🗑 **Phone Cleanup** – Deletes photos from the device after transfer  
- 🖼 **Carousel Photo Viewer** – Browse transferred images with Previous/Next navigation  
- ✅ **Batch Selection & Export** – Export only selected images or all images to a chosen directory  
- 🔍 **Jump to Photo** – Quickly navigate to a specific photo index  
- 📂 **Custom Export Directory** – Choose where processed photos are saved  
- 💾 **Persistent Configuration** – Remembers your last used export folder and settings

## 🛠 Requirements

- Python **3.7+**
- Installed system **ADB** (Android Debug Bridge) or included `tools/` folder
- Dependencies:  
  - tkinter  
  - Pillow  
  - OpenCV  
  - shutil  
  - os  

Install required libraries:
```bash
pip install pillow opencv-python PyInstaller
```

## 🚀 Usage

Run the script:
```bash
python main.py
```

Use the interface to:
1. **Connect** your Samsung device (USB or Wireless)
2. **Live View** to preview your phone camera
3. **Capture** photos
4. **Scan Asset Tag** to create an organized folder
5. **Finish Processing** to store photos in the correct folder
6. **View / Export** processed images

## 📁 Folder Structure

- `captures/` → Temporary folder for pulled images  
- `tools/` → Contains ADB and helper tools  
- `scripts/` → Core program scripts  

## 💡 Notes

- Processed folders are protected from duplicate processing for the same asset tag  
- Deleted images on the phone are **permanent**  
- Ideal for workflows involving **asset tagging, inventory management, and mobile photo capture**

## 📷 Command to Build (Windows)

The program will not work without the following libraries installed. Ensure **Python** is in your system path:
```bash
pip install Pillow opencv-python PyInstaller
```

Run this inside the `SamsungScannerTool` folder:
```bash
pyinstaller --noconsole --onefile --clean --noconfirm ^
  --add-data "tools;tools" ^
  --add-data "captures;captures" ^
  --add-data "scripts;scripts" ^
  --collect-all PIL ^
  --hidden-import PIL.ImageTk ^
  --hidden-import PIL._tkinter_finder ^
  --icon "assets\icon.ico" ^
  --name "Samsung Scanner Tool" main.py
```
The compiled program will be in the `dist` folder. Move the `.exe` file into the parent directory.  
When you see the icon appear, the build was successful.
