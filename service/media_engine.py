"""Media operations shared by desktop and CLI; no input(), window or console access."""
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event

import ffmpeg
from pytubefix import YouTube

from utils.files import output_folder, publish_file, require_ffmpeg, safe_filename
from utils.inputs import time_seconds, valid_youtube_url


class Cancelled(Exception):
    pass


def _check(cancel):
    if cancel is not None and cancel.is_set():
        raise Cancelled()


def _report(callback, message, percent=None):
    if callback:
        callback(message, percent)


def _youtube(url, callback, cancel):
    if not valid_youtube_url(url):
        raise ValueError("Informe um link válido de vídeo do YouTube.")
    _check(cancel)
    _report(callback, "Consultando o YouTube…")
    def progress(stream, chunk, remaining):
        _check(cancel)
        size = stream.filesize or 0
        percent = max(0, min(100, (size - remaining) / size * 100)) if size > 0 else None
        _report(callback, "Baixando mídia…", percent)
    return YouTube(url, on_progress_callback=progress)


def _run(arguments, cancel):
    _check(cancel)
    # CREATE_NO_WINDOW also hides FFmpeg consoles in the Windows GUI build.
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    with subprocess.Popen(arguments, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          stdin=subprocess.DEVNULL, creationflags=flags) as process:
        try:
            while True:
                _check(cancel)
                try:
                    result = process.wait(timeout=0.2)
                    break
                except subprocess.TimeoutExpired:
                    continue
            if result:
                raise subprocess.CalledProcessError(result, arguments)
        except BaseException:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            raise


def video_info(url, *, callback=None, cancel=None):
    yt = _youtube(url, callback, cancel)
    info = {"title": yt.title, "author": yt.author, "duration": yt.length,
            "views": yt.views, "channel_id": yt.channel_id, "description": yt.description or ""}
    _check(cancel)
    return info


def download_video(url, quality="high", *, root=None, callback=None, cancel=None):
    if quality not in {"high", "low"}:
        raise ValueError("Qualidade inválida.")
    executable = require_ffmpeg() if quality == "high" else None
    yt = _youtube(url, callback, cancel)
    folder = output_folder("videos", root)
    destination = folder / (safe_filename(yt.title) + ".mp4")
    if destination.exists():
        raise FileExistsError()
    with TemporaryDirectory(prefix=".download-", dir=folder) as temporary:
        if quality == "high":
            video = yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True).order_by("resolution").last()
            audio = yt.streams.filter(adaptive=True, only_audio=True).order_by("abr").last()
            if video is None or audio is None:
                raise ValueError("Não há faixas compatíveis para este vídeo.")
            _check(cancel)
            video_path = video.download(output_path=temporary, filename="video.mp4")
            _check(cancel)
            audio_path = audio.download(output_path=temporary, filename="audio.media")
            _report(callback, "Unindo vídeo e áudio…")
            result = Path(temporary) / "result.mp4"
            _run([executable, "-nostdin", "-y", "-i", str(video_path), "-i", str(audio_path),
                  "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", str(result)], cancel)
        else:
            stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").first()
            if stream is None:
                raise ValueError("Não há MP4 de baixa resolução disponível.")
            _check(cancel)
            result = Path(stream.download(output_path=temporary, filename="video.mp4"))
        _check(cancel)
        _report(callback, "Salvando arquivo…")
        publish_file(result, destination)
    return destination


def download_audio(url, *, root=None, callback=None, cancel=None):
    executable = require_ffmpeg()
    yt = _youtube(url, callback, cancel)
    stream = yt.streams.get_audio_only()
    if stream is None:
        raise ValueError("Nenhuma faixa de áudio disponível.")
    folder = output_folder("audios", root)
    destination = folder / (safe_filename(yt.title) + ".mp3")
    if destination.exists():
        raise FileExistsError()
    with TemporaryDirectory(prefix=".download-", dir=folder) as temporary:
        _check(cancel)
        source = stream.download(output_path=temporary, filename="audio.media")
        result = Path(temporary) / "result.mp3"
        _report(callback, "Convertendo para MP3…")
        _run([executable, "-nostdin", "-y", "-i", str(source), "-q:a", "0", "-map", "0:a:0", str(result)], cancel)
        _check(cancel)
        publish_file(result, destination)
    return destination


def convert_gif(path, start_time, end_time, fps=10, width=480, *, root=None, callback=None, cancel=None):
    executable = require_ffmpeg()
    source = Path(path).resolve()
    if not source.is_file() or source.suffix.lower() != ".mp4":
        raise ValueError("Selecione um arquivo MP4 existente.")
    start, end = time_seconds(start_time), time_seconds(end_time)
    if end <= start:
        raise ValueError("O fim do trecho deve ser posterior ao início.")
    if type(fps) is not int or not 1 <= fps <= 60 or type(width) is not int or not 1 <= width <= 4096:
        raise ValueError("Use FPS entre 1 e 60 e largura entre 1 e 4096 pixels.")
    folder = output_folder("gifs", root)
    destination = folder / (safe_filename(source.stem) + ".gif")
    if destination.exists():
        raise FileExistsError()
    with TemporaryDirectory(prefix=".convert-", dir=folder) as temporary:
        palette = Path(temporary) / "palette.png"
        result = Path(temporary) / "result.gif"
        def video():
            return (ffmpeg.input(str(source), ss=start, t=end - start)
                    .filter("fps", fps).filter("scale", width, -1, flags="lanczos"))
        _report(callback, "Preparando as cores do GIF…")
        graph = video().filter("palettegen").output(str(palette)).overwrite_output().global_args("-nostdin")
        _run(ffmpeg.compile(graph, cmd=executable), cancel)
        _report(callback, "Criando seu GIF…")
        graph = (ffmpeg.filter([video(), ffmpeg.input(str(palette))], "paletteuse")
                 .output(str(result)).overwrite_output().global_args("-nostdin"))
        _run(ffmpeg.compile(graph, cmd=executable), cancel)
        _check(cancel)
        publish_file(result, destination)
    return destination
