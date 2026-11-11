"""Create a local Linux launcher without changing desktop or system settings."""
import sys
from pathlib import Path


def create_shortcut(root: Path) -> Path:
    executable = root / 'venv' / 'bin' / 'python'
    if not executable.is_file():
        raise FileNotFoundError('Install the project virtual environment first.')
    def quoted(value):
        return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%') + '"'
    target = root / 'YouTube Converter.desktop'
    content = ('[Desktop Entry]\nType=Application\nName=YouTube Converter\n'
               'Comment=Baixar vídeos e áudio e converter MP4 para GIF\n'
               f'Exec={quoted(executable)} {quoted(root / "desktop.py")}\n'
               f'Path={root}\nTerminal=false\nCategories=AudioVideo;Video;\n')
    target.write_text(content, encoding='utf-8')
    target.chmod(0o755)
    return target


if __name__ == '__main__':
    if sys.platform != 'linux':
        raise SystemExit('On Windows, double-click Start-Windows.vbs instead.')
    print(create_shortcut(Path(__file__).resolve().parents[1]))
