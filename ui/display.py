"""Shared Rich presentation for the terminal application."""
import shutil
import time

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from utils.log_utils import get_base_dir

cli = Console(theme=Theme({
    "accent": "bright_cyan",
    "muted": "grey70",
    "success": "bright_green",
    "warning": "bright_yellow",
}))

PAGES = {
    "Main menu": ("Seu próximo arquivo começa aqui.", "Escolha o que você quer fazer.", "cyan"),
    "Video Download": ("Vídeos do YouTube", "Escolha a qualidade ou consulte as informações do vídeo.", "cyan"),
    "Track Download": ("Só o áudio. Em MP3.", "Extraia a faixa de áudio de um vídeo do YouTube.", "magenta"),
    "GIF Converter": ("Um trecho. Um GIF.", "Converta um MP4 local com controle de corte, tamanho e FPS.", "green"),
}


def clear():
    cli.clear()


def sleep(sec: float) -> None:
    time.sleep(sec)


def _width() -> int:
    return min(cli.width, 88)


def headers(header: str) -> None:
    title, description, color = PAGES.get(header, (header, "", "cyan"))
    cli.print()
    cli.print(Panel(
        Group(
            Text("YOUTUBE / CONVERTER", style="bold bright_white"),
            Text("VÍDEO  /  ÁUDIO  /  GIF", style="muted"),
            Text(""),
            Text(title, style=f"bold {color}"),
            Text(description, style="muted"),
        ),
        box=box.ROUNDED,
        border_style=color,
        padding=(1, 2),
        width=_width(),
    ))


def menu_options(options, *, color="cyan", back_label="Voltar ao início") -> None:
    """Use a wrapping single-column layout, including on narrow terminals."""
    table = Table.grid(padding=(0, 1), expand=True)
    table.add_column(width=3, no_wrap=True)
    table.add_column(ratio=1)
    for key, label, description in options:
        text = Text(label, style="bold")
        if description:
            text.append("\n" + description, style="muted")
        table.add_row(Text(f"{key:02}", style=f"bold {color}"), text)
        table.add_row("", "")
    table.add_row(Text("00", style="muted"), Text(back_label, style="muted"))
    cli.print(Panel(table, title="[bold] O que vamos fazer? [/bold]", title_align="left",
                    box=box.ROUNDED, border_style="bright_black", padding=(1, 1), width=_width()))
    footer()


def footer() -> None:
    status = Text("FFmpeg ")
    available = bool(shutil.which("ffmpeg"))
    status.append("disponível" if available else "não encontrado no PATH", style="success" if available else "warning")
    status.append("  |  Sem telemetria", style="muted")
    cli.print(status)
    location = Text("Saída: ", style="muted")
    location.append(str(get_base_dir()), style="muted")
    cli.print(location, overflow="fold")
    cli.print()


def main_menu():
    menu_options([
        (1, "Baixar vídeo", "MP4 em alta qualidade ou em um arquivo menor."),
        (2, "Extrair áudio", "Salve a faixa do vídeo como MP3."),
        (3, "Criar um GIF", "Transforme um trecho de MP4 em uma animação."),
    ], back_label="Sair do aplicativo")


def show_splash():
    clear()
    headers("Main menu")
    cli.print(Panel(
        Group(
            Text("Seus arquivos, no seu computador.", style="bold"),
            Text("Downloads usam a rede do YouTube. A conversão de MP4 para GIF é local.", style="muted"),
            Text("Sem telemetria ou logs persistentes. Detalhes em PRIVACY.md.", style="muted"),
        ),
        title="[accent] Antes de começar [/accent]", title_align="left",
        box=box.ROUNDED, border_style="bright_black", padding=(1, 2), width=_width(),
    ))
    cli.print()


def loading():
    show_splash()
    input("Pressione Enter para começar... ")


def print_exit():
    cli.print(Panel(Text("Até a próxima! Seus arquivos continuam na pasta de saída.", style="accent"),
                    box=box.ROUNDED, border_style="bright_black", padding=(1, 2), width=_width()))


if __name__ == "__main__":
    headers("Main menu")
    main_menu()
