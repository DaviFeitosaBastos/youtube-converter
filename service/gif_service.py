from pathlib import Path

from service import media_engine
from service.video_service import _done, _progress
from ui.display import cli
from ui.validation import validate_path
from utils.inputs import time_seconds as _time_seconds
from utils.media import media_action


def _get_time_input(label: str) -> str:
    while True:
        value = input(f"{label} (HH:MM:SS): ").strip()
        try:
            _time_seconds(value)
            return value
        except ValueError:
            cli.print("[red]Horário inválido. Use HH:MM:SS (exemplo: 00:00:05).[/red]")


def _get_int_with_default(label: str, default: int, maximum: int = 4096) -> int:
    while True:
        value = input(f"{label} (padrão: {default}, máximo: {maximum}): ").strip()
        if not value:
            return default
        if value.isascii() and value.isdigit() and 0 < int(value) <= maximum:
            return int(value)
        cli.print(f"Digite um número entre 1 e {maximum}.")


@media_action
def convert_mp4_to_gif(path: str) -> None:
    if not validate_path(path):
        return
    if Path(path).suffix.lower() != ".mp4":
        cli.print("[red]Escolha um arquivo .mp4.[/red]")
        return
    start_time = _get_time_input("Início do trecho")
    while True:
        end_time = _get_time_input("Fim do trecho")
        if _time_seconds(end_time) > _time_seconds(start_time):
            break
        cli.print("[red]O fim do trecho deve ser posterior ao início.[/red]")
    fps = _get_int_with_default("FPS", 10, 60)
    width = _get_int_with_default("Largura (px)", 480)
    _done(media_engine.convert_gif(path, start_time, end_time, fps, width, callback=_progress))
