import shutil
from functools import wraps

from ui.display import cli
from utils.log_utils import get_logger
from utils.files import output_folder, publish_file, require_ffmpeg, safe_filename

log = get_logger(__name__)


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
