from service import media_engine
from service.video_service import _done, _progress
from utils.media import media_action


@media_action
def download_track_youtube(url: str) -> None:
    _done(media_engine.download_audio(url, callback=_progress))
