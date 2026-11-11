"""Optional native-window integration test: python -m tests.desktop_smoke.

Uses synthetic local media; no YouTube requests or personal files are accessed.
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

if os.name != "nt":
    os.environ.setdefault("QT_API", "pyside6")

import webview

import desktop
from ui.desktop_api import DesktopAPI


def run():
    with tempfile.TemporaryDirectory(prefix='converter-gui-test-') as temporary:
        root = Path(temporary)
        fixture = root / 'fixture.mp4'
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-f', 'lavfi', '-i', 'color=c=blue:s=64x64:r=10',
                        '-t', '2', '-c:v', 'mpeg4', str(fixture)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        api = DesktopAPI()
        api._root = root
        window = webview.create_window('Desktop integration test', html=desktop.load_page(), js_api=api,
                                       width=1120, height=820, min_size=(680, 600))
        api._window = window
        results = []
        def expect(expression, timeout=20):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if window.evaluate_js(expression):
                    return
                time.sleep(0.1)
            raise AssertionError(expression)
        def screenshot(name):
            directory = os.environ.get('CONVERTER_SCREENSHOTS')
            if not directory:
                return
            from PySide6.QtCore import QObject, QMetaObject, Qt, Slot
            class Capture(QObject):
                @Slot()
                def save(self):
                    target = Path(directory) / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    window.native.grab().save(str(target))
            capture = Capture()
            capture.moveToThread(window.native.thread())
            QMetaObject.invokeMethod(capture, 'save', Qt.ConnectionType.BlockingQueuedConnection)
            capture.deleteLater()
        def exercise():
            try:
                if not window.events.loaded.wait(timeout=20):
                    raise AssertionError('Window failed to load')
                expect("document.getElementById('browserNotice').hidden === true")
                expect("!document.getElementById('downloadButton').disabled")
                time.sleep(0.3)
                screenshot("desktop-youtube.png")
                window.evaluate_js("document.getElementById('urlInput').value='https://example.com/video'; document.getElementById('downloadButton').click()")
                expect("document.getElementById('statusText').textContent.includes('link válido')")
                window.evaluate_js("document.querySelector('[data-view=gif]').click(); document.getElementById('chooseFile').click()")
                expect("document.getElementById('fileName').textContent === 'fixture.mp4'")
                window.evaluate_js("document.getElementById('gifEnd').value='00:00:01'; document.getElementById('gifWidth').value='64'; document.getElementById('gifButton').click()")
                expect("document.getElementById('activityCard').dataset.status === 'success'", timeout=30)
                assert (root / 'gifs' / 'fixture.gif').read_bytes().startswith(b'GIF')
                time.sleep(0.3)
                screenshot('desktop-gif.png')
                for width in (680,1120):
                    window.resize(width,820)
                    time.sleep(0.2)
                    expect('document.documentElement.scrollWidth <= window.innerWidth')
                window.evaluate_js("document.getElementById('privacyButton').click()")
                expect("document.getElementById('privacyDialog').open")
                results.append(True)
                print('Native window, JS/Python bridge, validation, file selection, real GIF conversion, responsive layout and privacy dialog: OK', flush=True)
            except Exception as error:
                results.append(False)
                print(f'Desktop smoke test failed: {error}', flush=True)
            finally:
                window.destroy()
        with patch.object(window, 'create_file_dialog', return_value=(str(fixture),)):
            webview.start(exercise, gui='edgechromium' if os.name == 'nt' else 'qt', private_mode=True)
        if results != [True]:
            raise SystemExit(1)


if __name__ == '__main__':
    run()
