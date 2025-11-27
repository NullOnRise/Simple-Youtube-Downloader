import os
from pathlib import Path
import PyInstaller.__main__

BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "app.py"

BIN_DIR = BASE_DIR / "bin"
YT_DLP_EXE = BIN_DIR / "yt-dlp.exe"
FFMPEG_EXE = BIN_DIR / "ffmpeg.exe"

args = [
    str(MAIN_SCRIPT),
    "--name", "yt_dlp_gui",
    "--noconfirm",
    "--windowed",
    "--onefile",
    "--clean",
    "--noupx",
    f"--add-binary={YT_DLP_EXE};bin",
    f"--add-binary={FFMPEG_EXE};bin",
]

if os.name != "nt":
    args.remove("--windowed")
    args.remove("--onefile")

PyInstaller.__main__.run(args)
