import contextlib
import io
import logging
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from service import gif_service, track_service, video_service
from ui import validation
from utils import log_utils, media
from utils.progress import make_progress_callback


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        environment = patch.dict(os.environ, {'YOUTUBE_CONVERTER_DATA_DIR': str(self.root)})
        environment.start()
        self.addCleanup(environment.stop)
        prompt = patch('builtins.input', return_value='')
        prompt.start()
        self.addCleanup(prompt.stop)

    def test_portable_names(self):
        for value in ['Artist / Song: live?', '..', 'CON', 'NUL.mp4', 'LPT1', 'é' * 200, '🎸' * 120, 'a\\b', 'line\nname']:
            with self.subTest(value=value):
                name = media.safe_filename(value)
                self.assertTrue(name)
                self.assertLessEqual(len(name.encode()), 121)
                self.assertNotRegex(name, r'[<>:"/\\|?*\x00-\x1f]')
                self.assertFalse(name.endswith((' ', '.')))
        self.assertEqual(media.safe_filename('CON'), '_CON')

    def test_exclusive_publish_preserves_existing_file(self):
        source, target = self.root / 'source', self.root / 'target'
        source.write_bytes(b'new')
        target.write_bytes(b'old')
        with self.assertRaises(FileExistsError):
            media.publish_file(source, target)
        self.assertEqual(target.read_bytes(), b'old')

    def test_failed_publish_removes_partial_file(self):
        source, target = self.root / 'source', self.root / 'target'
        source.write_bytes(b'new')
        def fail(stream, output):
            output.write(b'partial')
            raise OSError('disk full')
        with patch.object(shutil, 'copyfileobj', side_effect=fail):
            with self.assertRaises(OSError):
                media.publish_file(source, target)
        self.assertFalse(target.exists())
        self.assertTrue(source.exists())

    def test_output_folder_created_lazily(self):
        self.assertFalse((self.root / 'videos').exists())
        self.assertEqual(media.output_folder('videos'), self.root / 'videos')
        self.assertTrue((self.root / 'videos').is_dir())

    def test_linux_user_data_path(self):
        with patch.dict(os.environ, {'XDG_DATA_HOME': str(self.root)}, clear=True), patch.object(log_utils.sys, 'platform', 'linux'):
            self.assertEqual(log_utils.get_base_dir(), self.root / 'youtube-converter')

    def test_windows_user_data_path(self):
        with patch.dict(os.environ, {'LOCALAPPDATA': str(self.root)}, clear=True), patch.object(log_utils.sys, 'platform', 'win32'):
            self.assertEqual(log_utils.get_base_dir(), self.root / 'youtube-converter')

    def test_logs_do_not_create_files(self):
        logger = log_utils.get_logger('privacy-test')
        self.assertFalse(any(isinstance(h, logging.FileHandler) for h in logger.handlers))
        self.assertFalse((self.root / 'app.log').exists())

    def test_external_errors_do_not_leak_details(self):
        with patch.object(video_service, 'YouTube', side_effect=RuntimeError('https://secret-url/?token=private')), patch.object(media.log, 'error') as error:
            video_service.download_low_res('https://youtu.be/abcdefghijk')
        self.assertNotIn('secret', str(error.call_args))
        self.assertNotIn('private', str(error.call_args))

    def test_download_failure_cleans_all_temporaries(self):
        yt = MagicMock()
        yt.title = 'Artist / Song'
        stream = yt.streams.filter.return_value.order_by.return_value.last.return_value
        def download(output_path, filename):
            result = Path(output_path) / filename
            result.write_bytes(b'media')
            if filename == 'audio.media':
                raise OSError('connection failed')
            return str(result)
        stream.download.side_effect = download
        with patch.object(video_service, 'YouTube', return_value=yt), patch.object(video_service, 'require_ffmpeg', return_value='ffmpeg'):
            video_service.download_high_res('mock')
        self.assertEqual(list((self.root / 'videos').iterdir()), [])

    def test_merge_failure_leaves_no_final_or_temporary_output(self):
        yt = MagicMock()
        yt.title = 'Artist / Song'
        stream = yt.streams.filter.return_value.order_by.return_value.last.return_value
        def download(output_path, filename):
            result = Path(output_path) / filename
            result.write_bytes(b'media')
            return str(result)
        def merge(args, **kwargs):
            Path(args[-1]).write_bytes(b'partial')
            raise subprocess.CalledProcessError(1, args)
        stream.download.side_effect = download
        with patch.object(video_service, 'YouTube', return_value=yt), patch.object(video_service, 'require_ffmpeg', return_value='ffmpeg'), patch.object(video_service.subprocess, 'run', side_effect=merge):
            video_service.download_high_res('mock')
        self.assertEqual(list((self.root / 'videos').iterdir()), [])

    def test_missing_ffmpeg_is_handled(self):
        with patch.object(media.shutil, 'which', return_value=None):
            gif_service.convert_mp4_to_gif('missing.mp4')
            track_service.download_track_youtube('mock')
            video_service.download_high_res('mock')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_cancelled_download_cleans_temporaries(self):
        yt = MagicMock()
        yt.title = 'Cancelled'
        stream = yt.streams.filter.return_value.order_by.return_value.last.return_value
        def download(output_path, filename):
            (Path(output_path) / filename).write_bytes(b'partial')
            raise KeyboardInterrupt()
        stream.download.side_effect = download
        with patch.object(video_service, 'YouTube', return_value=yt), patch.object(video_service, 'require_ffmpeg', return_value='ffmpeg'):
            with self.assertRaises(KeyboardInterrupt):
                video_service.download_high_res('mock')
        self.assertEqual(list((self.root / 'videos').iterdir()), [])

    def test_unreadable_file_picker_returns_to_menu(self):
        with patch.object(Path, 'iterdir', side_effect=PermissionError()):
            self.assertIsNone(validation.pick_file(self.root, '.mp4'))

    def test_valid_urls_without_network(self):
        with patch('pytubefix.YouTube', side_effect=AssertionError('must not access network')):
            for url in ['https://youtu.be/dQw4w9WgXcQ', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'https://youtube.com/shorts/dQw4w9WgXcQ']:
                self.assertTrue(validation.url_validate(url), url)

    def test_reject_deceptive_or_invalid_urls(self):
        for url in ['https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ', 'https://evilyoutu.be/dQw4w9WgXcQ', 'https://youtube.com@evil.test/watch?v=dQw4w9WgXcQ', 'https://user@youtube.com/watch?v=dQw4w9WgXcQ', 'file:///tmp/movie.mp4', 'https://youtube.com', 'https://[broken', 'https://youtube.com:bad/watch?v=dQw4w9WgXcQ']:
            self.assertFalse(validation.url_validate(url), url)

    def test_invalid_timestamps(self):
        for value in ['00:99:99', '-1:00:00', 'hello', '00:00', '00:60:00', '00:00:²']:
            with self.assertRaises(ValueError):
                gif_service._time_seconds(value)
        self.assertEqual(gif_service._time_seconds('01:02:03'), 3723)

    def test_only_regular_files_and_case_insensitive_extension(self):
        (self.root / 'folder.mp4').mkdir()
        source = self.root / 'movie.MP4'
        source.touch()
        with patch('builtins.input', return_value='1'):
            self.assertEqual(validation.pick_file(self.root, '.mp4'), source)
        with patch.object(validation, 'sleep'):
            self.assertIsNone(validation.validate_path(str(self.root)))

    def test_actual_menu_options(self):
        with patch.object(validation, 'sleep'):
            self.assertIsNone(validation.track_input_validated(2))
            self.assertIsNone(validation.gif_input_validated(3))

    def test_zero_size_progress(self):
        with contextlib.redirect_stdout(io.StringIO()):
            make_progress_callback()(MagicMock(filesize=0), b'', 0)

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for local integration')
    def test_real_ffmpeg_download_conversions_and_gif(self):
        source = self.root / 'fixture.mp4'
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-f', 'lavfi', '-i', 'color=c=blue:s=64x64:r=10',
                        '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=44100', '-t', '2',
                        '-c:v', 'mpeg4', '-c:a', 'aac', str(source)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        yt = MagicMock()
        yt.title = 'Artist / Song: live?'
        stream = MagicMock()
        def download(output_path, filename):
            target = Path(output_path) / filename
            shutil.copyfile(source, target)
            return str(target)
        stream.download.side_effect = download
        yt.streams.filter.return_value.order_by.return_value.last.return_value = stream
        yt.streams.filter.return_value.order_by.return_value.first.return_value = stream
        yt.streams.get_audio_only.return_value = stream
        with patch.object(video_service, 'YouTube', return_value=yt):
            video_service.download_high_res('mock')
        videos = list((self.root / 'videos').glob('*.mp4'))
        self.assertEqual(len(videos), 1)
        self.assertGreater(videos[0].stat().st_size, 0)
        yt.title = 'Low resolution'
        with patch.object(video_service, 'YouTube', return_value=yt):
            video_service.download_low_res('mock')
        self.assertEqual(len(list((self.root / 'videos').glob('*.mp4'))), 2)
        with patch.object(track_service, 'YouTube', return_value=yt):
            track_service.download_track_youtube('mock')
        audios = list((self.root / 'audios').glob('*.mp3'))
        self.assertEqual(len(audios), 1)
        self.assertGreater(audios[0].stat().st_size, 0)
        palette = self.root / 'palette.png'
        palette.write_bytes(b'user file must survive')
        with patch('builtins.input', side_effect=['00:00:00', '00:00:00', '00:00:01', '', '', '']):
            gif_service.convert_mp4_to_gif(str(source))
        gifs = list((self.root / 'gifs').glob('*.gif'))
        self.assertEqual(len(gifs), 1)
        self.assertEqual(gifs[0].read_bytes()[:3], b'GIF')
        self.assertEqual(palette.read_bytes(), b'user file must survive')
        self.assertFalse(list(self.root.rglob('.download-*')))
        self.assertFalse(list(self.root.rglob('.convert-*')))


if __name__ == '__main__':
    unittest.main()
