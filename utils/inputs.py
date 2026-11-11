from urllib.parse import urlparse

from pytubefix.exceptions import RegexMatchError
from pytubefix.extract import video_id


def valid_youtube_url(url: str) -> bool:
    if not isinstance(url, str) or len(url) > 2048:
        return False
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        allowed = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be", "www.youtu.be"}
        if parsed.scheme not in {"http", "https"} or host not in allowed or parsed.username or parsed.password or parsed.port not in (None, 80, 443):
            return False
        video_id(url)
        return True
    except (ValueError, RegexMatchError):
        return False


def time_seconds(value: str) -> int:
    if not isinstance(value, str) or len(value) > 12:
        raise ValueError("Use HH:MM:SS")
    parts = value.split(":")
    if len(parts) != 3 or any(not p.isascii() or not p.isdigit() for p in parts):
        raise ValueError("Use HH:MM:SS")
    hours, minutes, seconds = map(int, parts)
    if minutes > 59 or seconds > 59:
        raise ValueError("Minutes and seconds must be between 00 and 59")
    return hours * 3600 + minutes * 60 + seconds
