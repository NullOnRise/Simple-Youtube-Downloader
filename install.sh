#!/usr/bin/env bash

set -e

echo "=== YT-DLP GUI Installer (Linux/macOS) ==="
echo

mkdir -p bin

echo "[1] Downloading yt-dlp..."
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o bin/yt-dlp
chmod +x bin/yt-dlp

echo "[2] Setting up FFmpeg..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected — installing via Homebrew (requires brew)..."
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew not found. Please install Homebrew or FFmpeg manually."
    else
        brew install ffmpeg || true
        if command -v ffmpeg >/dev/null 2>&1; then
            ln -sf "$(command -v ffmpeg)" bin/ffmpeg
        fi
    fi
else
    echo "Linux detected — trying apt (you may need sudo)..."
    if command -v ffmpeg >/dev/null 2>&1; then
        echo "FFmpeg already installed, linking..."
        ln -sf "$(command -v ffmpeg)" bin/ffmpeg
    else
        if command -v apt >/dev/null 2>&1; then
            sudo apt update
            sudo apt install -y ffmpeg
            ln -sf "$(command -v ffmpeg)" bin/ffmpeg
        else
            echo "No apt detected. Please install FFmpeg manually and ensure 'ffmpeg' is in PATH."
        fi
    fi
fi

echo "[3] Installing Python dependencies..."
pip install PyQt5 requests pyinstaller

echo
echo "[4] Verifying installation..."
if [[ -f bin/yt-dlp ]]; then
    echo "✓ yt-dlp installed in bin/yt-dlp"
else
    echo "✗ yt-dlp missing in bin/"
fi

if [[ -f bin/ffmpeg || -L bin/ffmpeg ]]; then
    echo "✓ FFmpeg linked in bin/ffmpeg"
else
    echo "✗ FFmpeg not found in bin/. You may need to install it manually."
fi

echo
echo "Done. You can now run:"
echo "    python app.py"
