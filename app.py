import sys
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QMessageBox,
    QSplitter,
    QFileDialog,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

BASE_DIR = Path(__file__).resolve().parent
BIN_DIR = BASE_DIR / "bin"

if os.name == "nt":
    import winreg
    YT_DLP_PATH = BIN_DIR / "yt-dlp.exe"
    FFMPEG_PATH = BIN_DIR / "ffmpeg.exe"
    
else:
    YT_DLP_PATH = BIN_DIR / "yt-dlp"
    FFMPEG_PATH = BIN_DIR / "ffmpeg"

DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "yt-dlp-gui"
DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

def register_url_protocol(command: str):
    if os.name != "nt":
        return

    key_base = r"Software\Classes\ytdlp"
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_base) as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, "URL:YTDLP Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

        shell_key = key_base + r"\shell\open\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, shell_key) as cmd_key:
            winreg.SetValueEx(cmd_key, None, 0, winreg.REG_SZ, command)
    except OSError:
        pass


def ensure_protocol_registered():
    if os.name != "nt":
        return

    key_cmd = r"Software\Classes\ytdlp\shell\open\command"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_cmd) as key:
            value, _ = winreg.QueryValueEx(key, None)
            if value:
                return
    except FileNotFoundError:
        pass

    if getattr(sys, "frozen", False):
        command = f'"{sys.executable}" "%1"'
    else:
        script_path = os.path.abspath(__file__)
        command = f'"{sys.executable}" "{script_path}" "%1"'

    register_url_protocol(command)


class DownloadWorker(QThread):
    status_changed = pyqtSignal(int, str)

    def __init__(self, index, item_data, download_dir: Path, parent=None):
        super().__init__(parent)
        self.index = index
        self.item_data = item_data
        self.download_dir = download_dir

    def run(self):
        url = self.item_data["url"]
        fmt = self.item_data["format"]
        output_template = str(self.download_dir / "%(title)s.%(ext)s")

        cmd = [
            str(YT_DLP_PATH),
            "-o", output_template,
            "--ffmpeg-location", str(BIN_DIR),
        ]

        if fmt == "mp3":
            cmd += ["-f", "bestaudio/best", "-x", "--audio-format", "mp3"]
        else:
            cmd += ["-f", "bv*+ba/b", "--merge-output-format", "mp4"]

        cmd.append(url)

        self.status_changed.emit(self.index, "Descargando...")

        try:
            kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True}
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            result = subprocess.run(cmd, **kwargs)
            if result.returncode == 0:
                self.status_changed.emit(self.index, "Completado")
            else:
                self.status_changed.emit(self.index, "Error (ver consola)")
        except Exception as e:
            self.status_changed.emit(self.index, f"Error: {e}")


class MainWindow(QMainWindow):
    def __init__(self, initial_special_url: str | None = None):
        super().__init__()

        self.setWindowTitle("Simple Youtube Downloader")
        self.resize(1000, 550)

        self.items = []
        self.thumbnails = {}
        self.workers = []
        self.download_dir = DEFAULT_DOWNLOAD_DIR

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Pega una URL de YouTube o ytdlp://<ID_VIDEO>")

        self.format_combo = QComboBox()
        self.format_combo.addItem("MP4 (vídeo)", userData="mp4")
        self.format_combo.addItem("MP3 (audio)", userData="mp3")

        self.add_button = QPushButton("Añadir a la cola")
        self.download_button = QPushButton("Descargar todo")
        self.thumb_button = QPushButton("Guardar miniatura")
        self.choose_folder_button = QPushButton("Carpeta descargas")

        self.list_widget = QListWidget()

        self.thumbnail_label = QLabel("Miniatura")
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setMinimumSize(320, 180)
        self.thumbnail_label.setScaledContents(True)

        self.folder_label = QLabel(str(self.download_dir))
        self.folder_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.build_ui()
        self.connect_signals()
        self.apply_style()

        if initial_special_url:
            self.url_edit.setText(initial_special_url)
            self.add_video_to_queue(auto_from_special=True)

    def build_ui(self):
        title_label = QLabel("YT-DLP Downloader")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; margin-bottom: 4px;")

        subtitle_label = QLabel("Descarga vídeos de YouTube como MP4 o MP3, con cola y miniaturas.")
        subtitle_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        subtitle_label.setStyleSheet("font-size: 12px; color: #9aa0a6; margin-bottom: 8px;")

        header_layout = QVBoxLayout()
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("URL:"))
        controls_layout.addWidget(self.url_edit, 1)
        controls_layout.addWidget(QLabel("Formato:"))
        controls_layout.addWidget(self.format_combo)
        controls_layout.addWidget(self.add_button)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.download_button)
        actions_layout.addWidget(self.thumb_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.choose_folder_button)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Descargar en:"))
        folder_layout.addWidget(self.folder_label, 1)

        left_layout = QVBoxLayout()
        left_layout.addLayout(header_layout)
        left_layout.addSpacing(8)
        left_layout.addLayout(controls_layout)
        left_layout.addSpacing(6)
        left_layout.addLayout(actions_layout)
        left_layout.addSpacing(6)
        left_layout.addLayout(folder_layout)
        left_layout.addSpacing(10)
        left_layout.addWidget(self.list_widget)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        right_layout = QVBoxLayout()
        thumb_title = QLabel("Vista previa de miniatura")
        thumb_title.setStyleSheet("font-size: 13px; font-weight: 500;")
        right_layout.addWidget(thumb_title)
        right_layout.addWidget(self.thumbnail_label, 1)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        container.setLayout(main_layout)

        self.setCentralWidget(container)

    def connect_signals(self):
        self.add_button.clicked.connect(self.add_video_to_queue)
        self.download_button.clicked.connect(self.download_all)
        self.thumb_button.clicked.connect(self.save_current_thumbnail)
        self.choose_folder_button.clicked.connect(self.choose_download_folder)
        self.list_widget.currentRowChanged.connect(self.show_thumbnail_for_row)

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #202124; color: #e8eaed; }
            QWidget { background-color: #202124; color: #e8eaed; font-family: Segoe UI, Roboto, sans-serif; font-size: 12px; }
            QLineEdit, QComboBox, QListWidget, QLabel { background-color: #303134; border-radius: 6px; padding: 4px; border: 1px solid #3c4043; }
            QListWidget { padding: 6px; }
            QPushButton { background-color: #1a73e8; color: white; border-radius: 6px; padding: 6px 12px; border: none; }
            QPushButton:hover { background-color: #2b82f6; }
            QPushButton:disabled { background-color: #5f6368; }
            QSplitter::handle { background-color: #3c4043; }
        """)
        self.thumbnail_label.setStyleSheet("QLabel { background-color: #171717; border: 1px solid #3c4043; border-radius: 8px; }")
        self.folder_label.setStyleSheet("background: transparent; border: none; color: #9aa0a6;")

    @staticmethod
    def parse_special_scheme(url: str) -> str:
        url = url.strip()
        if url.startswith("ytdlp://"):
            video_id = url[len("ytdlp://"):]
            return f"https://www.youtube.com/watch?v={video_id}"
        return url

    @staticmethod
    def extract_video_id(url: str) -> str | None:
        try:
            parsed = urlparse(url)
            if "youtu.be" in parsed.netloc:
                return parsed.path.lstrip("/")
            qs = parse_qs(parsed.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]
        except Exception:
            pass
        return None

    def get_thumbnail_pixmap(self, video_id: str) -> QPixmap | None:
        if video_id in self.thumbnails:
            return self.thumbnails[video_id]

        urls = [
            f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        ]

        for u in urls:
            try:
                resp = requests.get(u, timeout=10)
                if resp.status_code == 200:
                    pix = QPixmap()
                    pix.loadFromData(resp.content)
                    self.thumbnails[video_id] = pix
                    return pix
            except Exception:
                continue

        return None

    def fetch_title(self, url: str, video_id: str | None) -> str:
        if not YT_DLP_PATH.exists():
            return video_id or "Video"

        try:
            kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True, "timeout": 20}
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            result = subprocess.run([str(YT_DLP_PATH), "--get-title", url], **kwargs)
            title = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
            if title:
                return title
        except Exception:
            pass

        return video_id or "Video"

    def add_video_to_queue(self, auto_from_special: bool = False):
        raw_url = self.url_edit.text().strip()
        if not raw_url:
            QMessageBox.warning(self, "Error", "La URL está vacía.")
            return

        normalized_url = self.parse_special_scheme(raw_url)
        video_id = self.extract_video_id(normalized_url)

        if not video_id:
            QMessageBox.warning(self, "Error", "No se ha podido extraer el ID del vídeo.")
            return

        fmt = self.format_combo.currentData()
        title = self.fetch_title(normalized_url, video_id)

        item_data = {"url": normalized_url, "video_id": video_id, "format": fmt, "title": title, "status": "En cola"}

        index = len(self.items)
        self.items.append(item_data)

        display_fmt = "MP3" if fmt == "mp3" else "MP4"
        item_text = f"[{display_fmt}] {title} — ({item_data['status']})"
        list_item = QListWidgetItem(item_text)
        list_item.setData(Qt.UserRole, index)
        self.list_widget.addItem(list_item)

        if not auto_from_special:
            self.url_edit.clear()

        pix = self.get_thumbnail_pixmap(video_id)
        if pix and index == self.list_widget.currentRow():
            self.thumbnail_label.setPixmap(pix)
        elif self.list_widget.currentRow() == -1 and index == 0:
            self.list_widget.setCurrentRow(0)

    def show_thumbnail_for_row(self, row: int):
        if row < 0 or row >= len(self.items):
            self.thumbnail_label.setText("Miniatura")
            self.thumbnail_label.setPixmap(QPixmap())
            return

        video_id = self.items[row]["video_id"]
        pix = self.get_thumbnail_pixmap(video_id)
        if pix:
            self.thumbnail_label.setPixmap(pix)
        else:
            self.thumbnail_label.setText("Miniatura no disponible")
            self.thumbnail_label.setPixmap(QPixmap())

    def choose_download_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de descargas", str(self.download_dir))
        if path:
            self.download_dir = Path(path)
            self.download_dir.mkdir(parents=True, exist_ok=True)
            self.folder_label.setText(str(self.download_dir))

    def save_current_thumbnail(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.items):
            QMessageBox.information(self, "Info", "Selecciona un vídeo de la lista.")
            return

        video_id = self.items[row]["video_id"]
        title = self.items[row]["title"] or video_id
        pix = self.get_thumbnail_pixmap(video_id)
        if not pix:
            QMessageBox.warning(self, "Error", "No se ha podido obtener la miniatura.")
            return

        base = title.strip() or video_id
        invalid = '<>:"/\\|?*'
        safe = "".join(c for c in base if c not in invalid)
        if not safe:
            safe = video_id
        filename = safe + ".jpg"
        path = self.download_dir / filename

        if pix.save(str(path), "JPG"):
            QMessageBox.information(self, "Miniatura guardada", f"Miniatura guardada en:\n{path}")
        else:
            QMessageBox.warning(self, "Error", "No se ha podido guardar la miniatura.")

    def download_all(self):
        if not self.items:
            QMessageBox.information(self, "Info", "No hay vídeos en la cola.")
            return

        if not YT_DLP_PATH.exists():
            QMessageBox.critical(self, "Error", f"No se ha encontrado yt-dlp en: {YT_DLP_PATH}")
            return

        for index, item in enumerate(self.items):
            if item["status"].startswith("Completado") or item["status"].startswith("Descargando"):
                continue

            worker = DownloadWorker(index, item, self.download_dir)
            worker.status_changed.connect(self.update_item_status)
            self.workers.append(worker)
            worker.start()

    def update_item_status(self, index: int, status: str):
        if 0 <= index < len(self.items):
            self.items[index]["status"] = status
            list_item = self.list_widget.item(index)
            if list_item:
                fmt = self.items[index]["format"]
                display_fmt = "MP3" if fmt == "mp3" else "MP4"
                new_text = f"[{display_fmt}] {self.items[index]['title']} — ({status})"
                list_item.setText(new_text)


def main():
    initial_special_url = None
    if len(sys.argv) > 1 and sys.argv[1].startswith("ytdlp://"):
        initial_special_url = sys.argv[1]
    ensure_protocol_registered()
    app = QApplication(sys.argv)
    window = MainWindow(initial_special_url=initial_special_url)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
