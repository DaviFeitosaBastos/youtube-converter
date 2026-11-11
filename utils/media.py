import re
import shutil
from functools import wraps
from pathlib import Path

from ui.display import cli
from utils.log_utils import get_base_dir, get_logger

log = get_logger(__name__)


def safe_filename(title: str, fallback: str = "media") -> str:
    """Produce a portable filename, including Windows reserved-name handling."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f]', "_", str(title))
    name = name.strip(" .").encode("utf-8")[:120].decode("utf-8", errors="ignore").rstrip(" .") or fallback
    if name.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
        name = "_" + name
    return name


def output_folder(name: str) -> Path:
    folder = get_base_dir() / name
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def require_ffmpeg() -> str:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise FileNotFoundError("ffmpeg")
    return executable


def publish_file(source: Path, destination: Path) -> None:
    """Never overwrite existing media; remove incomplete copies on failure."""
    with destination.open("xb") as target:
        try:
            with source.open("rb") as stream:
                shutil.copyfileobj(stream, target)
        except BaseException:
            target.close()
            destination.unlink(missing_ok=True)
            raise


def media_action(function):
    """Keep failures at external boundaries from terminating the menu."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except FileExistsError:
            cli.print("[yellow]O arquivo já existe. Nenhum arquivo foi sobrescrito.[/yellow]")
        except FileNotFoundError:
            cli.print("[red]Arquivo ou FFmpeg não encontrado. Verifique o caminho e a instalação do FFmpeg.[/red]")
        except Exception:
            # Never persist external exception messages (they can include signed URLs).
            log.error("Não foi possível concluir. Verifique a conexão, a disponibilidade da mídia, as permissões e o FFmpeg.")
        try:
            input("Pressione Enter para voltar ao menu... ")
        except EOFError:
            pass
    return wrapped
