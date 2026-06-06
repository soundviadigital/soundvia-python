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

from soundvia import (
    SoundviaClient,
    OAuthClient,
    build_authorization_url,
    OAuthToken,
)
from soundvia.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError,
    InsufficientScopeError,
)


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


# ---------------------------------------------------------------------------
# SoundviaClient – public API
# ---------------------------------------------------------------------------

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
    def test_search_returns_typed_result(self):
        payload = {
            "ok": True,
            "query": "lofi",
            "tracks": [{"id": "t1", "title": "Lofi Rain", "artist_name": "chill guy", "stream_count": 42}],
            "releases": [],
            "artists": [],
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.search("lofi")
        self.assertEqual(result.query, "lofi")
        self.assertEqual(len(result.tracks), 1)
        self.assertEqual(result.tracks[0].title, "Lofi Rain")
        self.assertEqual(result.tracks[0].stream_count, 42)


class TestTracks(unittest.TestCase):
    def test_list_tracks(self):
        payload = {
            "ok": True,
            "tracks": [
                {"id": "t1", "title": "Track One", "genre": "lo-fi", "stream_count": 10},
                {"id": "t2", "title": "Track Two", "artist_name": "DJ X", "stream_count": 0},
            ],
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.list_tracks(q="something")
        self.assertEqual(len(result.tracks), 2)
        self.assertEqual(result.tracks[0].genre, "lo-fi")
        self.assertEqual(result.tracks[1].artist_name, "DJ X")

    def test_get_track(self):
        payload = {"track": {"id": "t42", "title": "Deep Dive", "cover_art": "https://cdn/img.jpg"}}
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            track = client.get_track("t42")
        self.assertEqual(track.id, "t42")
        self.assertEqual(track.cover_art, "https://cdn/img.jpg")

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
                "release_type": "ep",
                "artist_name": "The Band",
                "genre": "indie",
                "cover_art": "https://cdn/cover.jpg",
                "track_ids": ["t1", "t2"],
            }
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            release = client.get_release("r1")
        self.assertEqual(release.title, "Debut EP")
        self.assertEqual(release.release_type, "ep")
        self.assertEqual(release.artist_name, "The Band")
        self.assertEqual(release.track_ids, ["t1", "t2"])


class TestArtists(unittest.TestCase):
    def test_get_artist(self):
        payload = {
            "ok": True,
            "artist": {
                "id": "a1",
                "handle": "rebzyyx",
                "display_name": "rebzyyx",
                "avatar": "https://cdn/av.jpg",
                "bio": "music maker",
            },
            "tracks": [{"id": "t1", "title": "haha", "stream_count": 0}],
            "releases": [],
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            profile = client.get_artist("rebzyyx")
        self.assertEqual(profile.artist.handle, "rebzyyx")
        self.assertEqual(profile.artist.avatar, "https://cdn/av.jpg")
        self.assertEqual(profile.artist.bio, "music maker")
        self.assertEqual(len(profile.tracks), 1)


class TestPlaylists(unittest.TestCase):
    def test_list_playlists(self):
        payload = {
            "ok": True,
            "playlists": [{"id": "p1", "name": "Woah Mix", "track_ids": ["t1", "t2"]}],
        }
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.list_playlists(q="woah")
        self.assertEqual(result.playlists[0].name, "Woah Mix")
        self.assertEqual(result.playlists[0].track_ids, ["t1", "t2"])

    def test_get_playlist(self):
        payload = {"playlist": {"id": "p2", "name": "Late Night", "track_ids": []}}
        client = SoundviaClient("tok_test")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            pl = client.get_playlist("p2")
        self.assertEqual(pl.name, "Late Night")


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
        self.assertIn("superse", r)
        self.assertNotIn("supersecrettoken", r)


# ---------------------------------------------------------------------------
# build_authorization_url
# ---------------------------------------------------------------------------

class TestBuildAuthUrl(unittest.TestCase):
    def test_contains_required_params(self):
        url = build_authorization_url(
            client_id="svcli_abc",
            redirect_uri="https://myapp.com/cb",
            scope="user.read library.read",
            state="xyz",
        )
        self.assertIn("client_id=svcli_abc", url)
        self.assertIn("response_type=code", url)
        self.assertIn("state=xyz", url)
        self.assertIn("/oauth/authorize", url)

    def test_no_state_omitted(self):
        url = build_authorization_url("id", "https://x.com/cb", "user.read")
        self.assertNotIn("state=", url)


# ---------------------------------------------------------------------------
# OAuthClient
# ---------------------------------------------------------------------------

class TestOAuthClientFromCode(unittest.TestCase):
    def test_from_code_exchanges_token(self):
        token_payload = {
            "access_token": "svtok_abc",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "svref_xyz",
            "scope": "user.read",
        }
        with patch(URLOPEN, return_value=_mock_response(token_payload)):
            client = OAuthClient.from_code(
                client_id="svcli_x",
                client_secret="svsec_y",
                code="AUTH_CODE",
                redirect_uri="https://myapp.com/cb",
            )
        self.assertEqual(client.token.access_token, "svtok_abc")
        self.assertEqual(client.token.scope, "user.read")


class TestOAuthClientFromToken(unittest.TestCase):
    def test_from_token_sets_access_token(self):
        client = OAuthClient.from_token("svtok_direct")
        self.assertEqual(client.token.access_token, "svtok_direct")


class TestOAuthMe(unittest.TestCase):
    def test_me_returns_profile(self):
        payload = {
            "ok": True,
            "user": {
                "id": "u1",
                "username": "rebzyyx",
                "display_name": "rebzyyx",
                "avatar": "https://cdn/av.jpg",
                "role": "Artist",
                "email": "reb@example.com",
            },
        }
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            profile = client.me()
        self.assertEqual(profile.username, "rebzyyx")
        self.assertEqual(profile.email, "reb@example.com")
        self.assertEqual(profile.role, "Artist")


class TestOAuthLibrary(unittest.TestCase):
    def test_get_library(self):
        payload = {
            "ok": True,
            "library": [
                {
                    "library_key": "release:r1",
                    "item_type": "release",
                    "item_id": "r1",
                    "name": "My Album",
                    "track_count": 10,
                    "is_saved_item": True,
                    "is_owner": False,
                }
            ],
            "counts": {"total": 1, "saved_releases": 1, "saved_playlists": 0, "presaved_releases": 0},
        }
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.get_library()
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].item_type, "release")
        self.assertEqual(result.items[0].name, "My Album")
        self.assertEqual(result.counts.total, 1)

    def test_save_to_library(self):
        payload = {"ok": True, "saved": True, "type": "release", "id": "r1"}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            ok = client.save_to_library("release", "r1")
        self.assertTrue(ok)

    def test_remove_from_library(self):
        payload = {"ok": True, "removed": True}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            ok = client.remove_from_library("release", "r1")
        self.assertTrue(ok)


class TestOAuthPlaylists(unittest.TestCase):
    def test_get_playlists(self):
        payload = {
            "ok": True,
            "playlists": [
                {"id": "p1", "name": "My Mix", "track_count": 5, "is_owner": True, "visibility": "public"}
            ],
        }
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.get_playlists()
        self.assertEqual(result.playlists[0].name, "My Mix")
        self.assertTrue(result.playlists[0].is_owner)

    def test_create_playlist(self):
        payload = {"ok": True, "playlist": {"id": "p99", "name": "New Jams"}}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            pl = client.create_playlist("New Jams")
        self.assertEqual(pl.id, "p99")
        self.assertEqual(pl.name, "New Jams")

    def test_add_track(self):
        payload = {"ok": True, "added": True}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            ok = client.add_track_to_playlist("p1", "t1")
        self.assertTrue(ok)

    def test_remove_track(self):
        payload = {"ok": True, "removed": True}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            ok = client.remove_track_from_playlist("p1", "t1")
        self.assertTrue(ok)


class TestOAuthHistory(unittest.TestCase):
    def test_get_history(self):
        payload = {
            "ok": True,
            "history": [
                {"track_id": "t1", "played_at": "2025-01-01T12:00:00"},
                {"track_id": "t2", "played_at": "2025-01-01T11:00:00"},
            ],
        }
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.get_listening_history()
        self.assertEqual(len(result.history), 2)
        self.assertEqual(result.history[0].track_id, "t1")


class TestOAuthFollows(unittest.TestCase):
    def test_get_follows(self):
        payload = {"ok": True, "following_ids": ["u2", "u3"]}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.get_follows()
        self.assertEqual(result.following_ids, ["u2", "u3"])

    def test_follow(self):
        payload = {"ok": True, "followed": True}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            ok = client.follow("u5")
        self.assertTrue(ok)

    def test_unfollow(self):
        payload = {"ok": True, "unfollowed": True}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            ok = client.unfollow("u5")
        self.assertTrue(ok)


class TestOAuthNotifications(unittest.TestCase):
    def test_get_notifications(self):
        payload = {
            "ok": True,
            "notifications": [
                {"id": "n1", "type": "follow", "message": "Someone followed you", "read": False}
            ],
        }
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            result = client.get_notifications()
        self.assertEqual(len(result.notifications), 1)
        self.assertEqual(result.notifications[0].type, "follow")
        self.assertFalse(result.notifications[0].read)


class TestOAuthComments(unittest.TestCase):
    def test_post_comment(self):
        payload = {"ok": True, "comment_id": "c42"}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            comment_id = client.post_comment("t1", "great track!")
        self.assertEqual(comment_id, "c42")


class TestOAuthRefreshRevoke(unittest.TestCase):
    def test_refresh(self):
        new_token_payload = {
            "access_token": "svtok_new",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "svref_new",
            "scope": "user.read",
        }
        client = OAuthClient.from_token("svtok_old", refresh_token="svref_old")
        with patch(URLOPEN, return_value=_mock_response(new_token_payload)):
            new_tok = client.refresh()
        self.assertEqual(new_tok.access_token, "svtok_new")
        self.assertEqual(client.token.access_token, "svtok_new")

    def test_revoke(self):
        payload = {"ok": True, "revoked": True}
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, return_value=_mock_response(payload)):
            ok = client.revoke()
        self.assertTrue(ok)


class TestInsufficientScope(unittest.TestCase):
    def test_403_raises_insufficient_scope(self):
        client = OAuthClient.from_token("svtok_abc")
        with patch(URLOPEN, side_effect=_mock_http_error(403, {"error_description": "Scope user.email is required"})):
            with self.assertRaises(InsufficientScopeError):
                client.me()


if __name__ == "__main__":
    unittest.main()
