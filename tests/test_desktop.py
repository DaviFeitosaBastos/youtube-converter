import os
import tempfile
import unittest
from pathlib import Path
from threading import Event
from unittest.mock import MagicMock, patch

import desktop
from service import media_engine
from ui.desktop_api import DesktopAPI

URL = 'https://youtu.be/dQw4w9WgXcQ'


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        environment = patch.dict(os.environ, {'YOUTUBE_CONVERTER_DATA_DIR': str(self.root)})
        environment.start()
        self.addCleanup(environment.stop)
        self.api = DesktopAPI()

    def wait(self):
        self.api._thread.join(timeout=10)
        self.assertFalse(self.api._thread.is_alive())
        return self.api.state()

    def test_page_is_bundled_without_http_or_remote_assets(self):
        page = desktop.load_page()
        self.assertIn('<style>', page)
        self.assertNotIn('src="script.js"', page)
        self.assertNotIn('href="style.css"', page)
        self.assertNotIn('fonts.googleapis.com', page)
        self.assertIn('pywebviewready', page)

    def test_download_has_no_terminal_input_and_returns_result(self):
        result = self.root / 'videos' / 'test.mp4'
        with patch.object(media_engine, 'download_video', return_value=result) as download, patch('builtins.input', side_effect=AssertionError('Terminal input forbidden')):
            self.assertTrue(self.api.start_download(URL, 'mp4', 'low')['ok'])
            state = self.wait()
        self.assertEqual(state['status'], 'success')
        self.assertEqual(state['result']['path'], str(result))
        self.assertEqual(download.call_args.args, (URL, 'low'))

    def test_audio_routes_to_shared_engine(self):
        with patch.object(media_engine, 'download_audio', return_value=self.root / 'song.mp3') as download:
            self.api.start_download(URL)
            self.assertEqual(self.wait()['status'], 'success')
        download.assert_called_once()

    def test_invalid_url_and_unsupported_format_rejected_before_work(self):
        self.assertFalse(self.api.start_download('https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ')['ok'])
        self.assertFalse(self.api.start_download(URL, 'wav')['ok'])
        self.assertEqual(self.api.state()['status'], 'idle')

    def test_reject_parallel_jobs_and_cancel(self):
        started = Event()
        def download(url, **kwargs):
            started.set()
            kwargs['cancel'].wait(timeout=5)
            raise media_engine.Cancelled()
        with patch.object(media_engine, 'download_audio', side_effect=download):
            self.api.start_download(URL)
            self.assertTrue(started.wait(timeout=5))
            self.assertFalse(self.api.start_info(URL)['ok'])
            self.api.cancel()
            self.assertEqual(self.wait()['status'], 'cancelled')

    def test_external_error_details_are_not_exposed(self):
        with patch.object(media_engine, 'download_audio', side_effect=RuntimeError('secret-token=123')):
            self.api.start_download(URL)
            state = self.wait()
        self.assertEqual(state['status'], 'error')
        self.assertNotIn('secret-token', str(state))

    def test_existing_output_error_is_visible(self):
        with patch.object(media_engine, 'download_audio', side_effect=FileExistsError()):
            self.api.start_download(URL)
            state = self.wait()
        self.assertIn('já existe', state['message'])

    def test_state_is_a_copy(self):
        state = self.api.state()
        state['status'] = 'running'
        self.assertEqual(self.api.state()['status'], 'idle')

    def test_native_picker_cancellation_preserves_selection(self):
        source = self.root / 'clip.MP4'
        source.touch()
        self.api._selected_file = source
        self.api._window = MagicMock()
        self.api._window.create_file_dialog.return_value = None
        with patch.dict('sys.modules', {'webview': MagicMock()}):
            self.assertTrue(self.api.choose_mp4()['cancelled'])
        self.assertEqual(self.api._selected_file, source)

    def test_native_picker_uses_only_selected_mp4(self):
        source = self.root / 'clip.MP4'
        source.touch()
        self.api._window = MagicMock()
        self.api._window.create_file_dialog.return_value = (str(source),)
        with patch.dict('sys.modules', {'webview': MagicMock()}):
            response = self.api.choose_mp4()
        self.assertEqual(response, {'ok': True, 'name': source.name})
        self.assertEqual(self.api._selected_file, source)

    def test_gif_requires_file_and_valid_parameters(self):
        self.assertFalse(self.api.start_gif('00:00:00', '00:00:01')['ok'])
        source = self.root / 'clip.mp4'
        source.touch()
        self.api._selected_file = source
        self.assertFalse(self.api.start_gif('00:99:00', '00:00:01')['ok'])
        self.assertFalse(self.api.start_gif('00:00:01', '00:00:00')['ok'])
        self.assertFalse(self.api.start_gif('00:00:00', '00:00:01', 61)['ok'])
        self.assertFalse(self.api.start_gif('00:00:00', '00:00:01', True)['ok'])
        with patch.object(media_engine, 'convert_gif', return_value=self.root / 'clip.gif') as convert:
            self.api.start_gif('00:00:00', '00:00:01')
            self.assertEqual(self.wait()['status'], 'success')
        self.assertEqual(convert.call_args.args, (source, '00:00:00', '00:00:01', 10, 480))

    def test_metadata_uses_no_terminal(self):
        metadata = {'title': '<script>do not execute</script>', 'author': 'author', 'description': 'description', 'duration': 1, 'views': 2}
        with patch.object(media_engine, 'video_info', return_value=metadata):
            self.api.start_info(URL)
            state = self.wait()
        self.assertEqual(state['result']['kind'], 'info')
        self.assertEqual(state['result']['title'], metadata['title'])

    def test_closing_during_operation_requests_cancel_first(self):
        with self.api._lock:
            self.api._state['status'] = 'running'
        self.assertFalse(self.api._on_closing())
        self.assertTrue(self.api._cancel_event.is_set())

    def test_progress_is_bounded(self):
        self.api._progress('download', 200)
        self.assertEqual(self.api.state()['percent'], 100)
        self.api._progress('conversion', None)
        self.assertIsNone(self.api.state()['percent'])


if __name__ == '__main__':
    unittest.main()
