import os
import sys
import json
import csv
import tempfile
import unittest
from unittest import mock
import importlib.util

# Dynamically load ffmpeg-split.py module
MODULE_NAME = "ffmpeg_split_mod"
MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ffmpeg-split.py"))
spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
ffmpeg_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ffmpeg_mod)


class TestFFmpegSplit(unittest.TestCase):
    def test_ceildiv(self):
        # Who knows if today Python works same as it did yesterday?..
        self.assertEqual(ffmpeg_mod.ceildiv(10, 3.1), 4)
        self.assertEqual(ffmpeg_mod.ceildiv(9.0, 3), 3)
        self.assertEqual(ffmpeg_mod.ceildiv(0, 5), 0)

    @mock.patch.object(ffmpeg_mod.subprocess, 'check_output', return_value=b"123.4560000\n")
    def test_get_video_length(self, mock_check_output):
        # Simulate ffprobe output
        length = ffmpeg_mod.get_video_length("dummy.mp4")
        self.assertEqual(length, 123)
        mock_check_output.assert_called_once()

    @mock.patch.object(ffmpeg_mod.subprocess, 'check_output', return_value=b"")
    def test_split_by_seconds_basic(self, mock_check_output):
        # Provide video_length to avoid calling ffprobe
        ffmpeg_mod.split_by_seconds(filename="video.mp4", split_length=10, video_length=25)
        # Expect 3 splits: 0-10, 10-10, 20-10
        expected_calls = [
            mock.call(['ffmpeg', '-i', 'video.mp4', '-vcodec', 'copy', '-acodec', 'copy',
                       '-ss', '0', '-t', '10', 'video-1-of-3.mp4']),
            mock.call(['ffmpeg', '-i', 'video.mp4', '-vcodec', 'copy', '-acodec', 'copy',
                       '-ss', '10', '-t', '10', 'video-2-of-3.mp4']),
            mock.call(['ffmpeg', '-i', 'video.mp4', '-vcodec', 'copy', '-acodec', 'copy',
                       '-ss', '20', '-t', '10', 'video-3-of-3.mp4']),
        ]
        mock_check_output.assert_has_calls(expected_calls, any_order=False)

    def test_split_by_seconds_negative(self):
        # Negative split_length should exit
        with self.assertRaises(SystemExit):
            ffmpeg_mod.split_by_seconds(filename="video.mp4", split_length=-5, video_length=20)

    @mock.patch.object(ffmpeg_mod.subprocess, 'check_output', return_value=b"")
    def test_split_by_seconds_too_short(self, mock_check_output):
        # video_length < split_length should exit
        with self.assertRaises(SystemExit):
            ffmpeg_mod.split_by_seconds(filename="video.mp4", split_length=30, video_length=20)

    @mock.patch.object(ffmpeg_mod.subprocess, 'check_output', return_value=b"")
    def test_split_by_manifest_json(self, mock_check_output):
        # Create temporary JSON manifest
        data = [
            {"start_time": 0, "length": 5, "rename_to": "part1"},
            {"start_time": 5, "length": 5, "rename_to": "part2"},
        ]
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(data, tmp)
        tmp.close()
        try:
            ffmpeg_mod.split_by_manifest(filename="video.mp4", manifest=tmp.name)
        finally:
            os.unlink(tmp.name)
        # Expect two calls
        expected_calls = [
            mock.call(['ffmpeg', '-i', 'video.mp4', '-vcodec', 'copy', '-acodec', 'copy', '-y',
                       '-ss', '0', '-t', '5', 'part1.mp4']),
            mock.call(['ffmpeg', '-i', 'video.mp4', '-vcodec', 'copy', '-acodec', 'copy', '-y',
                       '-ss', '5', '-t', '5', 'part2.mp4']),
        ]
        mock_check_output.assert_has_calls(expected_calls, any_order=False)

    @mock.patch.object(ffmpeg_mod.subprocess, 'check_output', return_value=b"")
    def test_split_by_manifest_json_end_time(self, mock_check_output):
        # JSON manifest using end_time instead of length
        data = [
            {"start_time": 0, "end_time": 4, "rename_to": "foo"}
        ]
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(data, tmp)
        tmp.close()
        try:
            ffmpeg_mod.split_by_manifest(filename="clip.avi", manifest=tmp.name)
        finally:
            os.unlink(tmp.name)
        expected = [
            mock.call(['ffmpeg', '-i', 'clip.avi', '-vcodec', 'copy', '-acodec', 'copy', '-y',
                       '-ss', '0', '-t', '4', 'foo.avi']),
        ]
        mock_check_output.assert_has_calls(expected)

    @mock.patch.object(ffmpeg_mod.subprocess, 'check_output', return_value=b"")
    def test_split_by_manifest_csv(self, mock_check_output):
        # Create CSV manifest
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        writer = csv.writer(tmp)
        writer.writerow(['start_time', 'length', 'rename_to'])
        writer.writerow([0, 3, 'segA'])
        writer.writerow([3, 2, 'segB'])
        tmp.close()
        try:
            ffmpeg_mod.split_by_manifest(filename="vid.webm", manifest=tmp.name)
        finally:
            os.unlink(tmp.name)
        expected = [
            mock.call(['ffmpeg', '-i', 'vid.webm', '-vcodec', 'copy', '-acodec', 'copy', '-y',
                       '-ss', '0', '-t', '3', 'segA.webm']),
            mock.call(['ffmpeg', '-i', 'vid.webm', '-vcodec', 'copy', '-acodec', 'copy', '-y',
                       '-ss', '3', '-t', '2', 'segB.webm']),
        ]
        mock_check_output.assert_has_calls(expected)

    def test_split_by_manifest_missing_file(self):
        with self.assertRaises(SystemExit):
            ffmpeg_mod.split_by_manifest(filename="video.mp4", manifest="nonexistent.json")

    def test_split_by_manifest_unsupported_ext(self):
        # Create temp file with unsupported extension
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        tmp.write("dummy")
        tmp.close()
        try:
            with self.assertRaises(SystemExit):
                ffmpeg_mod.split_by_manifest(filename="video.mp4", manifest=tmp.name)
        finally:
            os.unlink(tmp.name)

if __name__ == '__main__':
    unittest.main()
