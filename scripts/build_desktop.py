"""Build an unpack-and-run desktop directory for the current operating system."""
import os
import shutil
import sys
from importlib.metadata import PackageNotFoundError, distribution

from packaging.requirements import Requirement
from pathlib import Path

import PyInstaller.__main__


def copy_licenses(output):
    queue = ['pywebview', 'pytubefix', 'ffmpeg-python', 'rich']
    if sys.platform != 'win32':
        queue += ['PySide6', 'shiboken6', 'QtPy']
    seen = set()
    while queue:
        name = queue.pop()
        key = name.lower().replace('_', '-')
        if key in seen:
            continue
        seen.add(key)
        try:
            package = distribution(name)
        except PackageNotFoundError:
            continue
        for requirement in package.requires or []:
            dependency = Requirement(requirement)
            if dependency.marker is None or dependency.marker.evaluate():
                queue.append(dependency.name)
        for file in package.files or []:
            if any(part.lower() == 'licenses' or part.lower().startswith(('license', 'copying')) for part in file.parts):
                source = Path(package.locate_file(file))
                if source.is_file():
                    relative = Path(*[part for part in file.parts if part not in ('.', '..')])
                    target = output / 'third-party-licenses' / key / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    system = 'Windows' if sys.platform == 'win32' else 'Linux'
    name = f'YouTube-Converter-{system}'
    options = ['desktop.py', '--onedir', '--noconfirm', '--name', name,
               '--paths', '.', '--add-data', 'web:web',
               '--exclude-module', 'PyQt5', '--exclude-module', 'PyQt6',
               '--exclude-module', 'PySide2', '--exclude-module', 'tkinter']
    if system == 'Windows':
        options += ['--windowed', '--exclude-module', 'PySide6', '--exclude-module', 'qtpy']
    else:
        options += ['--hidden-import', 'PySide6.QtWebEngineCore',
                    '--hidden-import', 'PySide6.QtWebEngineWidgets',
                    '--hidden-import', 'PySide6.QtWebChannel',
                    '--copy-metadata', 'PySide6', '--copy-metadata', 'shiboken6']
    PyInstaller.__main__.run(options)
    output = root / 'dist' / name
    for filename in ['PRIVACY.md', 'README.pt-br.md', 'README.md', 'THIRD_PARTY.md']:
        shutil.copy2(root / filename, output / filename)
    copy_licenses(output)
    archive = shutil.make_archive(str(output), 'zip', root / 'dist', name)
    print(f'Desktop package: {archive}')


if __name__ == '__main__':
    main()
