from pathlib import Path
from tempfile import TemporaryDirectory

import ffmpeg

from ui.display import cli
from ui.validation import validate_path
from utils.media import media_action, output_folder, publish_file, require_ffmpeg, safe_filename


def _time_seconds(value: str) -> int:
    parts = value.split(":")
    if len(parts) != 3 or any(not p.isascii() or not p.isdigit() for p in parts):
        raise ValueError("Use HH:MM:SS")
    hours, minutes, seconds = map(int, parts)
    if minutes > 59 or seconds > 59:
        raise ValueError("Minutes and seconds must be between 00 and 59")
    return hours * 3600 + minutes * 60 + seconds


def _get_time_input(label: str) -> str:
    while True:
        value = input(f"{label} (HH:MM:SS): ").strip()
        try:
            _time_seconds(value)
            return value
        except ValueError:
            cli.print("[red]Invalid time. Use HH:MM:SS (example: 00:00:05).[/red]")


def _get_int_with_default(label: str, default: int, maximum: int = 4096) -> int:
    while True:
        value = input(f"{label} (default: {default}, maximum: {maximum}): ").strip()
        if not value:
            return default
        if value.isascii() and value.isdigit() and 0 < int(value) <= maximum:
            return int(value)
        cli.print(f"Enter a number between 1 and {maximum}.")


@media_action
def convert_mp4_to_gif(path: str) -> None:
    executable = require_ffmpeg()
    if not validate_path(path):
        return
    source = Path(path).resolve()
    if source.suffix.lower() != ".mp4":
        cli.print("[red]File must be a .mp4[/red]")
        return
    start = _time_seconds(_get_time_input("Start time"))
    while True:
        end = _time_seconds(_get_time_input("End time"))
        if end > start:
            break
        cli.print("[red]End time must be after start time.[/red]")
    fps = _get_int_with_default("FPS", 10, 60)
    width = _get_int_with_default("Width (px)", 480)
    folder = output_folder("gifs")
    destination = folder / (safe_filename(source.stem) + ".gif")
    if destination.exists():
        raise FileExistsError()
    with TemporaryDirectory(prefix=".convert-", dir=folder) as temporary:
        palette = Path(temporary) / "palette.png"
        result = Path(temporary) / "result.gif"
        def video():
            return (ffmpeg.input(str(source), ss=start, t=end - start)
                    .filter("fps", fps).filter("scale", width, -1, flags="lanczos"))
        (video().filter("palettegen").output(str(palette)).overwrite_output()
         .global_args("-nostdin").run(cmd=executable, quiet=True))
        (ffmpeg.filter([video(), ffmpeg.input(str(palette))], "paletteuse")
         .output(str(result)).overwrite_output().global_args("-nostdin")
         .run(cmd=executable, quiet=True))
        publish_file(result, destination)
    cli.print(f"Saved to: {destination}", markup=False)
    input("Press Enter to return to the menu...")
