# Third-party components

The source and packaged application use third-party software with its own licenses:

- [pywebview](https://github.com/r0x0r/pywebview): BSD-3-Clause.
- [PySide6 / Qt for Python](https://doc.qt.io/qtforpython-6/licenses.html):
  LGPLv3/GPLv3/commercial options, depending on the component. The Linux package
  uses dynamically linked Qt libraries. Preserve their notices and license files.
- [Qt WebEngine](https://doc.qt.io/qt-6/qtwebengine-licensing.html): includes
  Chromium and further third-party components; see the upstream notices.
- [pytubefix](https://github.com/JuanBindez/pytubefix): Unlicense.
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python): Apache-2.0.
- [Rich](https://github.com/Textualize/rich): MIT.
- [FFmpeg](https://ffmpeg.org/legal.html): external executable, not bundled;
  its license depends on the build installed by the user.
- [Microsoft Edge WebView2](https://developer.microsoft.com/microsoft-edge/webview2/):
  external Windows runtime, distributed under Microsoft's terms.

Transitive Python dependencies retain their own licenses. The packaging script
copies installed distribution license metadata into `third-party-licenses/`.
This document does not replace those licenses or change the original project's licensing.
