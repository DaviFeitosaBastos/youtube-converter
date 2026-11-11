# YouTube Converter

A Linux and Windows desktop application with a Brazilian Portuguese interface,
HTML/CSS/JavaScript frontend and a native **pywebview** window. Download MP4 videos,
extract MP3 audio and convert local MP4 files to GIF without using a terminal in
everyday operation. [Documentação em português](README.pt-br.md).

## Features

- High-quality or low-resolution YouTube MP4 downloads.
- MP3 extraction and video metadata lookup.
- Local MP4-to-GIF conversion with trim, FPS and width controls.
- Native file/output-folder dialogs, per-stage progress and cancellation.
- Errors shown inside the window; one operation at a time, no file overwrites.
- Optional Rich terminal interface preserved in `main.py`.

`web/` is the application's working frontend. Opening its HTML in a browser only
previews the layout; operations require the desktop window. Communication uses
pywebview's in-process bridge, without an application HTTP server or REST API.

## Open without a terminal

Download your platform's ZIP from GitHub Actions artifacts or a release and
**extract the whole directory**. Keep `_internal` beside the executable.

- Windows: double-click `YouTube-Converter-Windows.exe`. Microsoft Edge WebView2
  Runtime must be installed.
- Linux: open `YouTube-Converter-Linux` using your file manager; allow execution
  in file properties if needed. Qt is bundled, but normal Linux graphics libraries
  remain required. CI builds on Ubuntu 24.04; other distributions may need a local build.

**FFmpeg must be installed and available in PATH.** It is not bundled. The window
reports a missing installation. Packaged applications do not require Python.

## Run from source

Initial setup requires Python 3.11+ and terminal commands. Everyday use can then
use a launcher.

```bash
python -m venv venv
```

Linux:

```bash
./venv/bin/python -m pip install -r requirements-desktop.txt
./venv/bin/python scripts/create_shortcut.py
```

Open the generated `YouTube Converter.desktop`. Your desktop may require marking
it executable/trusted in the file manager. Regenerate it if you move the project.

Windows (PowerShell):

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-desktop.txt
```

Double-click `Start-Windows.vbs` to launch the virtual environment's `pythonw.exe`
without a console (requires Windows Script Host). Alternatively, create a shortcut
to `venv\Scripts\pythonw.exe desktop.py` with the project as working directory.

For development, use the virtual environment's Python:

```bash
python desktop.py
```

Linux uses PySide6/QtWebEngine; Windows uses Edge Chromium. See the official
[pywebview installation guide](https://pywebview.flowrl.com/guide/installation)
and [FFmpeg downloads](https://ffmpeg.org/download.html) for system prerequisites.

## Usage and storage

Choose **YouTube**, paste a URL and select MP4 or MP3. Choose **MP4 para GIF** for
local conversion; select an MP4 using the native file picker and enter start/end
as `HH:MM:SS`. **Alterar** selects an output folder for this session, while
**Abrir pasta** opens the file manager.

Progress is per stage and can restart for the next stream. Conversion/merging uses
indeterminate progress. Cancellation may wait for the current network request or
stage. Closing a busy window requests cancellation; wait, then close again.

Default media location: `~/.local/share/youtube-converter` on Linux (respecting
`XDG_DATA_HOME`) or `%LOCALAPPDATA%\youtube-converter` on Windows. Override with
`YOUTUBE_CONVERTER_DATA_DIR`. Files go into `videos/`, `audios/` and `gifs/`.
Existing files from previous versions are never moved or deleted automatically.

## Optional CLI

```bash
python -m pip install -r requirements.txt
python main.py --check
python main.py
```

## Tests and packaging

```bash
python -m tests
python desktop.py --check
python -m tests.desktop_smoke
python -m pip install -r requirements-build.txt
python scripts/build_desktop.py
```

The native-window test needs a graphical environment and FFmpeg. It uses synthetic
local media, without accessing YouTube or personal files. Headless Linux testing
can use Qt offscreen with software rendering; do not disable Chromium's sandbox.

Build output: `dist/YouTube-Converter-Linux.zip` or
`dist/YouTube-Converter-Windows.zip`. Build on the target OS. CI tests Python 3.11
and 3.14 on both platforms and builds desktop packages on pushes to `main` and
manual runs. Tags `v*` publish releases after tests and builds succeed.

## Privacy and AI assistance

No accounts, telemetry, persistent URL history or application file logs. The
window loads local assets and uses a private profile. YouTube operations contact
YouTube/Google servers; MP4-to-GIF conversion runs locally. Read
[PRIVACY.md](PRIVACY.md) for data use, third parties, retention, deletion and limits
of the technical measures supporting LGPD principles.

OpenAI Codex assisted with review, fixes, tests, the desktop interface, CI and
documentation. This does not imply the original project was entirely AI-generated.
The running application does not call generative AI APIs or send URLs/media to AI services.

Only process content you are authorized to use and respect service terms and
other people's rights. Third-party components are listed in [THIRD_PARTY.md](THIRD_PARTY.md).

## Structure

- `desktop.py`: native window and bundled frontend loading.
- `web/`: desktop HTML, CSS and JavaScript.
- `ui/desktop_api.py`: bridge, native dialogs and background operations.
- `service/media_engine.py`: shared desktop/CLI media engine.
- `main.py`, `router.py`, `ui/display.py`: optional terminal interface.
- `scripts/`: Linux shortcut generation and desktop packaging.
- `tests/`: regressions, bridge tests and real-window/FFmpeg integration.

## Author

[Davi Feitosa Bastos](https://github.com/DaviFeitosaBastos)
