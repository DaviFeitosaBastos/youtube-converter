from service import media_engine
from ui.display import cli
from ui.validation import yes_or_not
from utils.media import media_action


def _progress(message, percent=None):
    if percent is None:
        cli.print(message)
    else:
        cli.print(f"\r{message} {percent:.0f}%", end="\r")


def _done(path):
    cli.print(f"\nSalvo em: {path}", markup=False)
    input("Pressione Enter para voltar ao menu... ")


@media_action
def get_video_info(url: str) -> None:
    info = media_engine.video_info(url)
    hours, remainder = divmod(info["duration"], 3600)
    minutes, seconds = divmod(remainder, 60)
    for label, value in [("Título", info["title"]), ("Duração", f"{hours:02}:{minutes:02}:{seconds:02}"),
                         ("Visualizações", info["views"]), ("Autor", info["author"]), ("ID do canal", info["channel_id"])]:
        cli.print(f"{label}: {value}", markup=False)
    if yes_or_not("Mostrar a descrição?"):
        cli.print(info["description"] or "Descrição indisponível.", markup=False)
    input("Pressione Enter para voltar ao menu... ")


@media_action
def download_high_res(url: str) -> None:
    _done(media_engine.download_video(url, "high", callback=_progress))


@media_action
def download_low_res(url: str) -> None:
    _done(media_engine.download_video(url, "low", callback=_progress))
