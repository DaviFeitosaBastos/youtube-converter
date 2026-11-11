import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from pytubefix import YouTube

from ui.display import cli
from utils.media import media_action, output_folder, publish_file, require_ffmpeg, safe_filename
from utils.progress import make_progress_callback


@media_action
def download_track_youtube(url: str) -> None:
    """Download and convert audio without retaining incomplete output."""
    executable = require_ffmpeg()
    yt = YouTube(url, on_progress_callback=make_progress_callback())
    stream = yt.streams.get_audio_only()
    if stream is None:
        raise ValueError("No audio stream")
    folder = output_folder("audios")
    destination = folder / (safe_filename(yt.title) + ".mp3")
    if destination.exists():
        raise FileExistsError()
    with TemporaryDirectory(prefix=".download-", dir=folder) as temporary:
        source = stream.download(output_path=temporary, filename="audio.media")
        result = Path(temporary) / "result.mp3"
        subprocess.run([executable, "-nostdin", "-y", "-i", str(source), "-q:a", "0", "-map", "0:a:0", str(result)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        publish_file(result, destination)
    cli.print(f"Salvo em: {destination}", markup=False)
    input("Pressione Enter para voltar ao menu... ")
