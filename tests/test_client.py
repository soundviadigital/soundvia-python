"""
Tests for the soundvia Python client.

Run with:  pytest tests/
"""
import json
import sys
import io
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from soundvia import SoundviaClient
from soundvia.exceptions import AuthenticationError, NotFoundError, RateLimitError, APIError


def _mock_response(data: dict, status: int = 200):
    body = json.dumps(data).encode()
    resp = MagicMock()
    resp.read.return_value = body
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _mock_http_error(status: int, body: dict | None = None):
    raw = json.dumps(body or {}).encode()
    err = HTTPError(url="", code=status, msg="", hdrs=MagicMock(), fp=io.BytesIO(raw))
    err.headers = {"Retry-After": "1"}
    return err


URLOPEN = "soundvia.client.urllib.request.urlopen"


class TestStatus(unittest.TestCase):
    def test_status_ok(self):
        payload = {
            "ok": True,
            "api": "v1",
            "app": {
                "id": "abc123",
                "name": "My App",
                "tier": "app",
                "verification_status": "pending",
                "limits": {"requests_per_minute": 180, "response_bytes_per_minute": 12582912},
            },
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.status()
        self.assertTrue(result.ok)
        self.assertEqual(result.app.name, "My App")
        self.assertEqual(result.app.limits.requests_per_minute, 180)

    def test_invalid_token_raises(self):
        client = SoundviaClient("bad_token")
        with patch(URLOPEN, side_effect=_mock_http_error(401)):
            with self.assertRaises(AuthenticationError):
                client.status()


class TestSearch(unittest.TestCase):
    def test_search_returns_result(self):
        payload = {
            "ok": True,
            "tracks": [{"id": "t1", "title": "Lofi Rain"}],
            "releases": [],
            "artists": [],
            "playlists": [],
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.search("lofi")
        self.assertEqual(len(result.tracks), 1)
        self.assertEqual(result.tracks[0]["title"], "Lofi Rain")


class TestTracks(unittest.TestCase):
    def test_list_tracks(self):
        payload = {
            "ok": True,
            "tracks": [
                {"id": "t1", "title": "Track One"},
                {"id": "t2", "title": "Track Two"},
            ],
            "total": 2,
            "limit": 20,
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.list_tracks(q="something")
        self.assertEqual(len(result.tracks), 2)
        self.assertEqual(result.tracks[0].title, "Track One")

    def test_get_track(self):
        payload = {"track": {"id": "t42", "title": "Deep Dive"}}
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            track = client.get_track("t42")
        self.assertEqual(track.id, "t42")
        self.assertEqual(track.title, "Deep Dive")

    def test_get_track_not_found(self):
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, side_effect=_mock_http_error(404, {"error": "Track not found"})):
            with self.assertRaises(NotFoundError):
                client.get_track("doesnotexist")


class TestReleases(unittest.TestCase):
    def test_get_release(self):
        payload = {
            "release": {
                "id": "r1",
                "title": "Debut EP",
                "type": "ep",
                "tracks": [],
            }
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            release = client.get_release("r1")
        self.assertEqual(release.title, "Debut EP")
        self.assertEqual(release.release_type, "ep")


class TestArtists(unittest.TestCase):
    def test_get_artist(self):
        payload = {
            "ok": True,
            "artist": {
                "id": "a1",
                "handle": "rebzyyx",
                "display_name": "rebzyyx",
            },
            "tracks": [{"id": "t1", "title": "haha"}],
            "releases": [],
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            profile = client.get_artist("rebzyyx")
        self.assertEqual(profile.artist.handle, "rebzyyx")
        self.assertEqual(len(profile.tracks), 1)
        self.assertEqual(profile.tracks[0].title, "haha")


class TestPlaylists(unittest.TestCase):
    def test_list_playlists(self):
        payload = {
            "ok": True,
            "playlists": [{"id": "p1", "title": "Woah Mix", "tracks": []}],
            "total": 1,
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.list_playlists(q="woah")
        self.assertEqual(result.playlists[0].title, "Woah Mix")


class TestRateLimit(unittest.TestCase):
    def test_rate_limit_retries_then_raises(self):
        err = _mock_http_error(429)
        client = SoundviaClient("tok_test", max_retries=1)
        with patch(URLOPEN, side_effect=err), patch("soundvia.client.time.sleep"):
            with self.assertRaises(RateLimitError):
                client.status()


class TestClientRepr(unittest.TestCase):
    def test_repr_masks_token(self):
        client = SoundviaClient("supersecrettoken")
        r = repr(client)
        self.assertIn("supers", r)
        self.assertNotIn("supersecrettoken", r)


if __name__ == "__main__":
    unittest.main()
