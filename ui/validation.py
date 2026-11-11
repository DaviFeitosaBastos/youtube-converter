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
        cli.print("[red]Enter a valid YouTube video URL.[/red]")
        return False


def yes_or_not(message: str) -> bool:
    """
    Prompts the user for a Y/N confirmation. Returns True if 'Y', False if 'N'.
    """
    while True:
        cli.print(Panel(f"[bold yellow]{message}[/bold yellow]",
                        border_style="yellow",
                        expand=False))

        choice = Prompt.ask("\n[bold green]Choice[/bold green]",
                            choices=["Y", "N", "y", "n"],
                            show_choices=True).strip().upper()

        if choice in ("Y", "N"):
            if choice == "Y":
                cli.print("[bold green]✔ Confirmed![/bold green]")
            else:
                cli.print("[bold red]✘ Cancelled![/bold red]")
            sleep(0.5)
            clear()
            return choice == "Y"

        cli.print("[bold red]✘ Invalid input! Please enter Y or N.[/bold red]")
        sleep(0.8)
        clear()


def get_int_input() -> int | None:
    """
    Reads an integer from user input. Returns None on invalid input.
    """
    while True:
        try:
            choice = int(Prompt.ask(f"\n[green]Choice[/green]"))
            clear()
            return choice
        except ValueError:
            log.warning("Invalid input: expected a number")
            sleep(0.5)
            return None



def validate_path(path: str) -> bool | None:
    p = Path(path)
    if p.is_file():
        return True
    else:
        cli.print("[red]This path doesn't exist[/red]")
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
        cli.print("[red]Cannot read this folder. Check its permissions.[/red]")
        return None

    if not files:
        cli.print(f"No {extension} files found in {folder}", markup=False)
        sleep(0.6)
        return None

    cli.print(f"\n[bold]Available {extension} files:[/bold]")
    for i, file in enumerate(files, start=1):
        cli.print(f"{i} - {file.name}", markup=False)

    while True:
        try:
            choice = int(input("\nChoice: "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            cli.print("[red]Invalid option![/red]")
            sleep(0.5)
        except ValueError:
            log.warning(f"Invalid input: expected number")
            sleep(0.5)


def main_input_validated(input_choice: int) -> int | None:

    if input_choice in [1, 2, 3, 0]:
        cli.print(f"\n[green]Option selected {input_choice}")
        sleep(1)
        return input_choice

    cli.print(f"[red]Invalid option")
    sleep(1)



def vd_input_validated(input_choice: int) -> int | None:

    if input_choice in [1, 2, 3, 0]:
        cli.print(f"\n[green]Option selected {input_choice}")
        sleep(1)
        return input_choice

    cli.print(f"[red]Invalid option")
    sleep(1)

def track_input_validated(input_choice: int) -> int | None:

    if input_choice in [1, 0]:
        cli.print(f"\n[green]Option selected {input_choice}")
        sleep(1)
        return input_choice

    cli.print(f"[red]Invalid option")
    sleep(1)

def gif_input_validated(input_choice: int) -> int | None:

    if input_choice in [1, 0]:
        cli.print(f"\n[green]Option selected {input_choice}")
        sleep(1)
        return input_choice

    cli.print(f"[red]Invalid option")
    sleep(1)

if __name__ == "__main__":
    yes_or_not("Wanna go back [Y/N]")
    pass
