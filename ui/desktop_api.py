"""Small, in-process bridge exposed only to the bundled desktop page."""
import copy
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from threading import Event, Lock, Thread

from service import media_engine
from utils.inputs import time_seconds, valid_youtube_url
from utils.log_utils import get_base_dir


class DesktopAPI:
    def __init__(self):
        self._window = None
        self._lock = Lock()
        self._cancel_event = Event()
        self._root = get_base_dir()
        self._selected_file = None
        self._thread = None
        self._state = {"status": "idle", "message": "Tudo pronto para começar.", "percent": None, "result": None}

    def settings(self):
        with self._lock:
            return {"output_dir": str(self._root), "ffmpeg": bool(shutil.which("ffmpeg"))}

    def state(self):
        with self._lock:
            return copy.deepcopy(self._state)

    def _progress(self, message, percent=None):
        if percent is not None:
            percent = max(0, min(100, float(percent))) if math.isfinite(float(percent)) else None
        with self._lock:
            if not self._cancel_event.is_set():
                self._state.update(message=message, percent=percent)

    def _start(self, operation):
        with self._lock:
            if self._state["status"] == "running":
                return {"ok": False, "message": "Aguarde a operação atual terminar."}
            self._cancel_event.clear()
            self._state = {"status": "running", "message": "Preparando…", "percent": None, "result": None}
            self._thread = Thread(target=self._work, args=(operation,), name="media-worker")
            self._thread.start()
        return {"ok": True}

    def _work(self, operation):
        try:
            result = operation()
            final = {"status": "success", "message": "Pronto! Operação concluída.", "percent": 100, "result": result}
        except media_engine.Cancelled:
            final = {"status": "cancelled", "message": "Operação cancelada.", "percent": None, "result": None}
        except FileExistsError:
            final = {"status": "error", "message": "Esse arquivo já existe na pasta de saída. Nenhum arquivo foi sobrescrito.", "percent": None, "result": None}
        except FileNotFoundError:
            final = {"status": "error", "message": "Arquivo ou FFmpeg não encontrado. Verifique o arquivo e a instalação do FFmpeg.", "percent": None, "result": None}
        except Exception:
            # External errors can include signed URLs, titles and local paths.
            final = {"status": "error", "message": "Não foi possível concluir. Confira a conexão, a disponibilidade da mídia, o FFmpeg e as permissões da pasta.", "percent": None, "result": None}
        with self._lock:
            self._state = final

    def start_download(self, url, format="mp3", quality="high"):
        if not valid_youtube_url(url):
            return {"ok": False, "message": "Cole um link válido de vídeo do YouTube."}
        if format not in ("mp3", "mp4") or quality not in ("high", "low"):
            return {"ok": False, "message": "Escolha MP3 ou MP4 e uma qualidade válida."}
        root = self._root
        def operation():
            options = {"root": root, "callback": self._progress, "cancel": self._cancel_event}
            path = (media_engine.download_audio(url, **options) if format == "mp3"
                    else media_engine.download_video(url, quality, **options))
            return {"kind": "file", "name": path.name, "path": str(path)}
        return self._start(operation)

    def start_info(self, url):
        if not valid_youtube_url(url):
            return {"ok": False, "message": "Cole um link válido de vídeo do YouTube."}
        def operation():
            info = media_engine.video_info(url, callback=self._progress, cancel=self._cancel_event)
            return {"kind": "info", **info}
        return self._start(operation)

    def choose_mp4(self):
        try:
            if self.state()["status"] == "running":
                return {"ok": False, "message": "Aguarde a operação atual terminar."}
            import webview
            selected = self._window.create_file_dialog(webview.FileDialog.OPEN, allow_multiple=False,
                                                       file_types=("Vídeos MP4 (*.mp4;*.MP4)",))
            if not selected:
                return {"ok": True, "cancelled": True}
            path = Path(selected[0]).resolve()
            if not path.is_file() or path.suffix.lower() != ".mp4":
                return {"ok": False, "message": "Selecione um arquivo MP4 existente."}
            self._selected_file = path
            return {"ok": True, "name": path.name}
        except Exception:
            return {"ok": False, "message": "Não foi possível abrir o seletor de arquivos."}

    def start_gif(self, start, end, fps=10, width=480):
        path = self._selected_file
        if path is None or not path.is_file():
            return {"ok": False, "message": "Primeiro escolha um arquivo MP4."}
        try:
            if time_seconds(end) <= time_seconds(start):
                raise ValueError()
        except (ValueError, TypeError):
            return {"ok": False, "message": "Use HH:MM:SS e um fim posterior ao início."}
        if type(fps) is not int or not 1 <= fps <= 60 or type(width) is not int or not 1 <= width <= 4096:
            return {"ok": False, "message": "Use FPS entre 1 e 60 e largura entre 1 e 4096 pixels."}
        root = self._root
        def operation():
            result = media_engine.convert_gif(path, start, end, fps, width, root=root,
                                               callback=self._progress, cancel=self._cancel_event)
            return {"kind": "file", "name": result.name, "path": str(result)}
        return self._start(operation)

    def choose_output(self):
        try:
            if self.state()["status"] == "running":
                return {"ok": False, "message": "Aguarde a operação atual terminar."}
            import webview
            selected = self._window.create_file_dialog(webview.FileDialog.FOLDER)
            if selected:
                self._root = Path(selected[0]).resolve()
            return {"ok": True, "output_dir": str(self._root)}
        except Exception:
            return {"ok": False, "message": "Não foi possível selecionar a pasta."}

    def open_output(self):
        try:
            self._root.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(str(self._root))
            else:
                subprocess.Popen(["xdg-open", str(self._root)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"ok": True}
        except Exception:
            return {"ok": False, "message": "Não foi possível abrir a pasta. O caminho aparece no rodapé."}

    def cancel(self):
        with self._lock:
            if self._state["status"] == "running":
                self._cancel_event.set()
                self._state.update(message="Cancelamento solicitado. Aguardando a etapa atual…", percent=None)
        return {"ok": True}

    def _on_closing(self):
        if self.state()["status"] == "running":
            self.cancel()
            return False
        return True
