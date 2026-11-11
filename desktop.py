"""Desktop entry point. No terminal or HTTP API is needed at runtime."""
import os
import sys
from pathlib import Path


def resource_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def load_page() -> str:
    root = resource_dir() / "web"
    page = (root / "index.html").read_text(encoding="utf-8")
    # Inline bundled assets: the bridge works without a local web server or file URLs.
    page = page.replace('<link rel="stylesheet" href="style.css" />',
                        '<style>' + (root / "style.css").read_text(encoding="utf-8") + '</style>')
    return page.replace('<script src="script.js"></script>',
                        '<script>' + (root / "script.js").read_text(encoding="utf-8") + '</script>')


def _startup_error():
    message = ("Não foi possível abrir o YouTube Converter. Verifique a instalação das dependências desktop "
               "e do renderizador gráfico conforme o README.pt-br.md.")
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, "YouTube Converter", 0x10)
        return
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "YouTube Converter", message)
    except Exception:
        if sys.stderr is not None:
            print(message, file=sys.stderr)


def main():
    try:
        if sys.platform == "linux":
            os.environ.setdefault("QT_API", "pyside6")
        import webview
        from ui.desktop_api import DesktopAPI
        if "--check" in sys.argv:
            load_page()
            return 0
        api = DesktopAPI()
        window = webview.create_window("YouTube Converter", html=load_page(), js_api=api,
                                       width=1120, height=820, min_size=(680, 600),
                                       background_color="#101114", text_select=True)
        api._window = window
        window.events.closing += api._on_closing
        renderer = "edgechromium" if sys.platform == "win32" else "qt"
        webview.start(gui=renderer, private_mode=True, debug=False)
        return 0
    except Exception:
        if "--check" in sys.argv:
            return 1
        _startup_error()
        return 1


if __name__ == "__main__":
    sys.exit(main())
