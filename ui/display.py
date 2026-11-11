from rich.console import Console
from rich.panel import Panel
import time

cli = Console()

def clear():
    cli.clear()

def sleep(sec: float) -> None :
    time.sleep(sec)
    return None

def show_splash():
    # Limpa a tela e mostra um painel de boas-vindas
    cli.clear()
    logo = """
[bold cyan]YT_CONVERSOR v1.1[/bold cyan]
[white]Midia | Tracks | GIF[/white]
    """
    cli.print(Panel(logo, expand=False, border_style="green"))
    sleep(1.5) # Tempo para o usuário ler


def loading():
    cli.print("[bold cyan]YouTube Converter[/bold cyan]")
    cli.print("Privacy: media stays on this computer. YouTube downloads use the network.")
    cli.print("No telemetry or persistent logs. See PRIVACY.md for details.")
    input("Press Enter to open the menu...")


def print_exit():
    msg = "Exiting!!!!!"
    for i in range(len(msg) + 1):
        clear()
        cli.print(f"[bold red on white]{msg[:i]}[/bold red on white]", end="\r")
        sleep(0.1)
    sleep(0.3)
    clear()


def headers(header: str) -> None:
    if header == "Video Download":
        cli.print("[red]=[/red]" * 32)
        cli.print(f"[red]{header.center(32)}[/red]" )
        cli.print("[red]=[/red]" * 32)

    elif header == "Track Download":
        cli.print("[purple]=[/purple]" * 32)
        cli.print(f"[purple]{header.center(32)}[/purple]" )
        cli.print("[purple]=[/purple]" * 32)

    elif header == "GIF Converter":
        cli.print("[cyan]=[/cyan]" * 32)
        cli.print(f"[cyan]{header.center(32)}[/cyan]")
        cli.print("[cyan]=[/cyan]" * 32)

    elif header == "Main menu":
        cli.print("[green]=[/green]" * 32)
        cli.print(f"[green]{header.center(32)}[/green]" )
        cli.print("[green]=[/green]" * 32)
    else:
        return None

def main_menu():
    cli.print("[green]1[/green] - Download videos from [red][[/red][red]YOU[/red]TUBE[red]][/red]")
    cli.print("[green]2[/green] - Get the audio tack from [red][[/red][red]YOU[/red]TUBE[red]][/red]")
    cli.print("[green]3[/green] - Convert MP4 to GIF")
    cli.print("[green]0[/green] - [yellow]Exit[/yellow]")



if __name__ == "__main__":
    main_menu()
