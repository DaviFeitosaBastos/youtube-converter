import logging
import os
import sys
from pathlib import Path

from rich.logging import RichHandler


def get_base_dir() -> Path:
    """Keep downloaded media in a writable, per-user data directory."""
    override = os.environ.get("YOUTUBE_CONVERTER_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "youtube-converter"


def get_logger(name: str) -> logging.Logger:
    # No persistent logs: URLs, titles, local paths and exceptions can contain personal data.
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(show_path=False, markup=False)
        handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
