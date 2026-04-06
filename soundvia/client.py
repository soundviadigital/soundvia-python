from __future__ import annotations

import urllib.parse
import urllib.request
import urllib.error
import json
import time
from typing import Any

from .exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError,
)
from .models import (
    StatusResult,
    SearchResult,
    Track,
    TrackListResult,
    Release,
    ReleaseListResult,
    ArtistProfileResult,
    Playlist,
    PlaylistListResult,
)

_BASE_URL = "https://soundvia.eu/api/v1"
_DEFAULT_TIMEOUT = 15
_DEFAULT_LIMIT = 20


class SoundviaClient:
    def __init__(
        self,
        token: str,
        *,
        base_url: str = _BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ) -> None:
        if not token:
            raise ValueError("A non-empty API token is required.")
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": "soundvia-python/1.0.0",
        }

    def _build_url(self, path: str, params: dict[str, Any] | None = None) -> str:
        url = f"{self._base_url}/{path.lstrip('/')}"
        if params:
            filtered = {k: str(v) for k, v in params.items() if v is not None}
            if filtered:
                url = f"{url}?{urllib.parse.urlencode(filtered)}"
        return url

    def _request(self, method: str, path: str, params: dict | None = None) -> dict:
        url = self._build_url(path, params)
        headers = self._headers()
        req = urllib.request.Request(url, headers=headers, method=method.upper())

        attempt = 0
        while True:
            attempt += 1
            try:
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    body = resp.read().decode("utf-8")
                    return json.loads(body)
            except urllib.error.HTTPError as exc:
                body = ""
                try:
                    body = exc.read().decode("utf-8")
                except Exception:
                    pass

                if exc.code == 401:
                    raise AuthenticationError(
                        "Invalid or missing API token. "
                        "Check that you passed the correct token to SoundviaClient."
                    ) from exc

                if exc.code == 404:
                    try:
                        msg = json.loads(body).get("error", "Resource not found.")
                    except Exception:
                        msg = "Resource not found."
                    raise NotFoundError(msg) from exc

                if exc.code == 429:
                    retry_after = None
                    try:
                        retry_after = int(exc.headers.get("Retry-After", 60))
                    except Exception:
                        retry_after = 60
                    if attempt <= self._max_retries:
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError(retry_after=retry_after) from exc

                if exc.code >= 500 and attempt <= self._max_retries:
                    time.sleep(2 ** attempt)
                    continue

                try:
                    msg = json.loads(body).get("error", str(exc))
                except Exception:
                    msg = str(exc)
                raise APIError(msg, status_code=exc.code) from exc

            except urllib.error.URLError as exc:
                if attempt <= self._max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise APIError(f"Network error: {exc.reason}") from exc

    def _get(self, path: str, params: dict | None = None) -> dict:
        return self._request("GET", path, params)

    def status(self) -> StatusResult:
        data = self._get("/status")
        return StatusResult.from_dict(data)

    def search(self, query: str, *, limit: int = _DEFAULT_LIMIT) -> SearchResult:
        data = self._get("/search", {"q": query, "limit": limit})
        return SearchResult.from_dict(data)

    def list_tracks(
        self,
        *,
        q: str | None = None,
        limit: int = _DEFAULT_LIMIT,
        offset: int = 0,
    ) -> TrackListResult:
        data = self._get("/tracks", {"q": q, "limit": limit, "offset": offset or None})
        return TrackListResult.from_dict(data)

    def get_track(self, track_id: str) -> Track:
        data = self._get(f"/tracks/{track_id}")
        track_data = data.get("track") or data
        return Track.from_dict(track_data)

    def list_releases(
        self,
        *,
        q: str | None = None,
        limit: int = _DEFAULT_LIMIT,
        offset: int = 0,
    ) -> ReleaseListResult:
        data = self._get("/releases", {"q": q, "limit": limit, "offset": offset or None})
        return ReleaseListResult.from_dict(data)

    def get_release(self, release_id: str) -> Release:
        data = self._get(f"/releases/{release_id}")
        release_data = data.get("release") or data
        return Release.from_dict(release_data)

    def get_artist(self, handle: str) -> ArtistProfileResult:
        data = self._get(f"/artists/{handle}")
        return ArtistProfileResult.from_dict(data)

    def list_playlists(
        self,
        *,
        q: str | None = None,
        limit: int = _DEFAULT_LIMIT,
        offset: int = 0,
    ) -> PlaylistListResult:
        data = self._get("/playlists", {"q": q, "limit": limit, "offset": offset or None})
        return PlaylistListResult.from_dict(data)

    def get_playlist(self, playlist_id: str) -> Playlist:
        data = self._get(f"/playlists/{playlist_id}")
        playlist_data = data.get("playlist") or data
        return Playlist.from_dict(playlist_data)

    def __repr__(self) -> str:
        masked = f"{self._token[:6]}{'*' * (len(self._token) - 6)}" if len(self._token) > 6 else "***"
        return f"SoundviaClient(token={masked!r}, base_url={self._base_url!r})"

    def __enter__(self) -> "SoundviaClient":
        return self

    def __exit__(self, *_: Any) -> None:
        pass
