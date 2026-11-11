import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from pytubefix import YouTube

from ui.display import cli
from ui.validation import yes_or_not
from utils.media import media_action, output_folder, publish_file, require_ffmpeg, safe_filename
from utils.progress import make_progress_callback


@media_action
def get_video_info(url: str) -> None:
    yt = YouTube(url)
    try:
        likes = yt.likes
    except Exception:
        likes = "Indisponível"
    hours, remainder = divmod(yt.length, 3600)
    minutes, seconds = divmod(remainder, 60)
    for label, value in [("Título", yt.title), ("Duração", f"{hours:02}:{minutes:02}:{seconds:02}"),
                         ("Visualizações", yt.views), ("Autor", yt.author), ("ID do canal", yt.channel_id), ("Curtidas", likes)]:
        cli.print(f"{label}: {value}", markup=False)
    if yes_or_not("Mostrar a descrição?"):
        cli.print(yt.description or "Descrição indisponível.", markup=False)
    input("Pressione Enter para voltar ao menu... ")


@media_action
def download_high_res(url: str) -> None:
    executable = require_ffmpeg()
    yt = YouTube(url, on_progress_callback=make_progress_callback())
    video = yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True).order_by("resolution").last()
    audio = yt.streams.filter(adaptive=True, only_audio=True).order_by("abr").last()
    if video is None or audio is None:
        raise ValueError("No compatible streams")
    folder = output_folder("videos")
    destination = folder / (safe_filename(yt.title) + ".mp4")
    if destination.exists():
        raise FileExistsError()
    cli.print("Baixando vídeo e áudio...")
    # All intermediate files and failed FFmpeg outputs disappear on exit or error.
    with TemporaryDirectory(prefix=".download-", dir=folder) as temporary:
        workspace = Path(temporary)
        video_path = video.download(output_path=temporary, filename="video.mp4")
        audio_path = audio.download(output_path=temporary, filename="audio.media")
        result = workspace / "result.mp4"
        subprocess.run([executable, "-nostdin", "-y", "-i", str(video_path), "-i", str(audio_path),
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", str(result)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        publish_file(result, destination)
    cli.print(f"Salvo em: {destination}", markup=False)
    input("Pressione Enter para voltar ao menu... ")


@media_action
def download_low_res(url: str) -> None:
    yt = YouTube(url, on_progress_callback=make_progress_callback())
    stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").first()
    if stream is None:
        raise ValueError("No compatible stream")
    folder = output_folder("videos")
    destination = folder / (safe_filename(yt.title) + ".mp4")
    if destination.exists():
        raise FileExistsError()
    with TemporaryDirectory(prefix=".download-", dir=folder) as temporary:
        source = stream.download(output_path=temporary, filename="video.mp4")
        publish_file(Path(source), destination)
    cli.print(f"Salvo em: {destination}", markup=False)
    input("Pressione Enter para voltar ao menu... ")
