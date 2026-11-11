from rich.prompt import Prompt
from rich.panel import Panel
from ui.display import sleep, clear, cli
from pytubefix.exceptions import RegexMatchError
from urllib.parse import urlparse
from pathlib import Path
from utils.log_utils import get_logger

log = get_logger(__name__)

def url_validate(url: str) -> bool:
    """
    Validate a YouTube video URL locally; the service checks availability.
    """
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        valid_host = host in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be", "www.youtu.be"}
        if parsed.scheme not in {"http", "https"} or not valid_host or parsed.username or parsed.password or parsed.port not in (None, 80, 443):
            raise ValueError("Invalid YouTube URL")
        # Let the downloader report availability; validation should not make duplicate requests.
        from pytubefix.extract import video_id
        video_id(url)
        return True
    except (ValueError, RegexMatchError):
        cli.print("[red]Informe um link válido de vídeo do YouTube.[/red]")
        return False


def yes_or_not(message: str) -> bool:
    """Keep Y/N compatibility while accepting S for Portuguese users."""
    cli.print(Panel(message, border_style="cyan", expand=False))
    choice = Prompt.ask("[accent]Confirmar[/accent]", choices=["s", "n", "y", "S", "N", "Y"])
    return choice.lower() in {"s", "y"}


def get_int_input() -> int | None:
    while True:
        value = Prompt.ask("[bold cyan]Digite uma opção[/bold cyan]")
        try:
            return int(value)
        except ValueError:
            cli.print("[yellow]Use o número de uma das opções acima.[/yellow]")


def validate_path(path: str) -> bool | None:
    p = Path(path)
    if p.is_file():
        return True
    else:
        cli.print("[red]Esse caminho não corresponde a um arquivo.[/red]")
        sleep(0.6)

def pick_file(folder: Path, extension: str) -> Path | None:
    """
    Lists files with the given extension in the folder and lets the user pick one.
    """
    try:
        files = sorted(
            (p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == extension.lower()),
            key=lambda p: p.name.lower(),
        ) if folder.is_dir() else []
    except OSError:
        cli.print("[red]Não foi possível abrir a pasta. Verifique as permissões.[/red]")
        return None

    if not files:
        cli.print(f"Nenhum arquivo {extension} encontrado em {folder}", markup=False)
        sleep(0.6)
        return None

    cli.print(f"\n[bold]Arquivos {extension} disponíveis:[/bold]")
    for i, file in enumerate(files, start=1):
        cli.print(f"{i} - {file.name}", markup=False)

    while True:
        try:
            choice = int(input("\nNúmero do arquivo: "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            cli.print("[red]Escolha um dos arquivos da lista.[/red]")
            sleep(0.5)
        except ValueError:
            cli.print("[yellow]Digite o número do arquivo.[/yellow]")
            sleep(0.5)


def _validate_choice(choice: int, allowed: tuple[int, ...]) -> int | None:
    if choice in allowed:
        return choice
    cli.print("[yellow]Essa opção não está no menu.[/yellow]")
    input("Pressione Enter para tentar novamente... ")
    return None


def main_input_validated(input_choice: int) -> int | None:
    return _validate_choice(input_choice, (0, 1, 2, 3))


def vd_input_validated(input_choice: int) -> int | None:
    return _validate_choice(input_choice, (0, 1, 2, 3))


def track_input_validated(input_choice: int) -> int | None:
    return _validate_choice(input_choice, (0, 1))


def gif_input_validated(input_choice: int) -> int | None:
    return _validate_choice(input_choice, (0, 1))
