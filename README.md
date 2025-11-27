Aquí lo tienes exactamente en el formato que pediste:

# YT-DLP GUI Downloader  
A modern YouTube downloader written in **Python + PyQt5**, supporting MP4, MP3, thumbnails, custom download folders, download queues, and a custom URL protocol:  
ytdlp://<VIDEO_ID>


<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-OK-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

</div>

---

## 🚀 Features

- Download YouTube content as:
  - **MP4** (best video + audio)
  - **MP3** (best audio)
- Add multiple videos to a **download queue**
- **Thumbnail preview** and ability to save thumbnails
- Choose a **custom download folder**
- Fully modern **dark UI**
- No console window on Windows
- Automatic registration of the custom protocol:

ytdlp://<VIDEO_ID>


allowing instant opening from browsers
- Fully buildable into a `.exe` using PyInstaller

---

## 📦 Requirements

### Python 3.9+

Install required Python modules:

```bash
pip install PyQt5 requests pyinstaller
````

### yt-dlp (must be downloaded manually)

Download the official binary from:

➡ [https://github.com/yt-dlp/yt-dlp/releases](https://github.com/yt-dlp/yt-dlp/releases)

Place it into the `bin` folder:

```
bin/yt-dlp.exe   (Windows)
bin/yt-dlp       (Linux/macOS)
```

### FFmpeg (must be downloaded manually)

Download FFmpeg from an official source:

➡ [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
Windows builds:
➡ [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

Place the FFmpeg binary here:

```
bin/ffmpeg.exe   (Windows)
bin/ffmpeg       (Linux/macOS)
```

---

## 📁 Directory Structure

```
/project
│
├─ yt_dlp_gui.py
├─ build.py
├─ install.cmd
├─ install.sh
└─ bin/
   ├─ yt-dlp.exe / yt-dlp
   └─ ffmpeg.exe / ffmpeg
```

---

## ▶️ Running the Application

Run using Python:

```bash
python yt_dlp_gui.py
```

You can open URLs like:

```text
ytdlp://dQw4w9WgXcQ
```

and the application will automatically launch and import the video.

---

## 🏗 Building a Windows Executable

Use the included PyInstaller build script:

```bash
python build.py
```

This creates:

```
dist/yt_dlp_gui.exe
```

---

## 🌐 Custom URL Protocol: ytdlp://

The application automatically installs a Windows custom URL protocol:

```
ytdlp://<VIDEO_ID>
```

For example:

```
ytdlp://bTqVqk7FSmY
```

This allows direct opening from browsers and external apps.

Admin privileges **not required** (uses HKCU registry).

---

## 🔧 Automatic Install Scripts

You can install all dependencies automatically using these remote commands:

### Linux / macOS

```bash
bash <(curl -sSL https://raw.githubusercontent.com/<YOUR_USERNAME>/<YOUR_REPO>/main/install.sh)
```

### Windows

```cmd
curl -L https://raw.githubusercontent.com/<YOUR_USERNAME>/<YOUR_REPO>/main/install.cmd -o install.cmd && install.cmd
```

Replace `<YOUR_USERNAME>` and `<YOUR_REPO>` with your GitHub account details.

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## ⭐ Contributions

Pull requests are welcome!
If you'd like new features (themes, auto-updater, presets, etc.), create an issue.

```
