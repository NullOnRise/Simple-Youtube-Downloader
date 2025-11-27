@echo off
setlocal enabledelayedexpansion
title YT-DLP GUI Installer (Windows)

echo === YT-DLP GUI Installer (Windows) ===
echo.

if not exist bin mkdir bin

echo [1] Downloading yt-dlp...
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -o bin\yt-dlp.exe

echo [2] Downloading FFmpeg (essentials build)...
curl -L https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-release-essentials.zip -o ffmpeg.zip

echo Extracting FFmpeg...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"

for /d %%a in (ffmpeg-*) do (
    if exist "%%a\bin\ffmpeg.exe" (
        copy /Y "%%a\bin\ffmpeg.exe" bin\ffmpeg.exe >nul
    )
)

del ffmpeg.zip
for /d %%a in (ffmpeg-*) do rmdir /s /q "%%a"

echo [3] Installing Python dependencies (PyQt5, requests, pyinstaller)...
pip install PyQt5 requests pyinstaller

echo.
echo [4] Verifying installation...

if exist bin\yt-dlp.exe (
    echo  ✓ yt-dlp installed at bin\yt-dlp.exe
) else (
    echo  ✗ yt-dlp.exe missing in bin\
)

if exist bin\ffmpeg.exe (
    echo  ✓ FFmpeg installed at bin\ffmpeg.exe
) else (
    echo  ✗ ffmpeg.exe missing in bin\
)

echo.
echo Done. You can now run:
echo     python yt_dlp_gui.py

echo.
pause
endlocal
