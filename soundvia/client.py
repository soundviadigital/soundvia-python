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
    InsufficientScopeError,
)
from .models import (
    # public API
    StatusResult,
    SearchResult,
    Track,
    TrackListResult,
    Release,
    ReleaseListResult,
    ArtistProfileResult,
    Playlist,
    PlaylistListResult,
    # OAuth user API
    OAuthToken,
    UserProfile,
    LibraryResult,
    UserPlaylist,
    UserPlaylistListResult,
    PlayHistoryResult,
    FollowsResult,
    NotificationsResult,
)

_BASE_URL = "https://soundvia.eu/api/v1"
_OAUTH_BASE_URL = "https://soundvia.eu"
_DEFAULT_TIMEOUT = 15
_DEFAULT_LIMIT = 20


# ---------------------------------------------------------------------------
# Shared HTTP mixin
# ---------------------------------------------------------------------------

class _HttpMixin:
    _base_url: str
    _timeout: int
    _max_retries: int

    def _headers(self) -> dict[str, str]:
        raise NotImplementedError

    def _build_url(self, base: str, path: str, params: dict[str, Any] | None = None) -> str:
        url = f"{base.rstrip('/')}/{path.lstrip('/')}"
        if params:
            filtered = {k: str(v) for k, v in params.items() if v is not None}
            if filtered:
                url = f"{url}?{urllib.parse.urlencode(filtered)}"
        return url

    def _request(
        self,
        method: str,
        url: str,
        body: dict | None = None,
    ) -> dict:
        headers = self._headers()
        data: bytes | None = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

        attempt = 0
        while True:
            attempt += 1
            try:
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw) if raw.strip() else {}
            except urllib.error.HTTPError as exc:
                raw_body = ""
                try:
                    raw_body = exc.read().decode("utf-8")
                except Exception:
                    pass

                if exc.code == 401:
                    raise AuthenticationError(
                        "Invalid or missing token. "
                        "Check that you passed the correct token."
                    ) from exc

                if exc.code == 403:
                    try:
                        msg = json.loads(raw_body).get("error_description", "Insufficient scope.")
                    except Exception:
                        msg = "Insufficient scope."
                    raise InsufficientScopeError(msg) from exc

                if exc.code == 404:
                    try:
                        msg = json.loads(raw_body).get("error", "Resource not found.")
                    except Exception:
                        msg = "Resource not found."
                    raise NotFoundError(msg) from exc

                if exc.code == 429:
                    retry_after = 60
                    try:
                        retry_after = int(exc.headers.get("Retry-After", 60))
                    except Exception:
                        pass
                    if attempt <= self._max_retries:
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError(retry_after=retry_after) from exc

                if exc.code >= 500 and attempt <= self._max_retries:
                    time.sleep(2 ** attempt)
                    continue

                try:
                    msg = json.loads(raw_body).get("error", str(exc))
                except Exception:
                    msg = str(exc)
                raise APIError(msg, status_code=exc.code) from exc

            except urllib.error.URLError as exc:
                if attempt <= self._max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise APIError(f"Network error: {exc.reason}") from exc


# ---------------------------------------------------------------------------
# Public API client  (app token)
# ---------------------------------------------------------------------------

class SoundviaClient(_HttpMixin):
    """
    Client for the Soundvia public API (``/api/v1/*``).

    Authenticate with your app token from soundvia.eu/developer::

        client = SoundviaClient("svapp_...")
    """

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
            "User-Agent": "soundvia-python/2.0.0",
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = self._build_url(self._base_url, path, params)
        return self._request("GET", url)

    # --- status ---

    def status(self) -> StatusResult:
        """Return app identity, tier, and current rate-limit config."""
        return StatusResult.from_dict(self._get("/status"))

    # --- search ---

    def search(self, query: str, *, limit: int = _DEFAULT_LIMIT) -> SearchResult:
        """Search tracks, releases, and artists with a single query."""
        return SearchResult.from_dict(self._get("/search", {"q": query, "limit": limit}))

    # --- tracks ---

    def list_tracks(
        self,
        *,
        q: str | None = None,
        limit: int = _DEFAULT_LIMIT,
    ) -> TrackListResult:
        """List public tracks, optionally filtered by ``q``."""
        return TrackListResult.from_dict(self._get("/tracks", {"q": q, "limit": limit}))

    def get_track(self, track_id: str) -> Track:
        """Return a single public track by ID."""
        data = self._get(f"/tracks/{track_id}")
        return Track.from_dict(data.get("track") or data)

    # --- releases ---

    def list_releases(
        self,
        *,
        q: str | None = None,
        limit: int = _DEFAULT_LIMIT,
    ) -> ReleaseListResult:
        """List public releases, optionally filtered by ``q``."""
        return ReleaseListResult.from_dict(self._get("/releases", {"q": q, "limit": limit}))

    def get_release(self, release_id: str) -> Release:
        """Return a single public release by ID."""
        data = self._get(f"/releases/{release_id}")
        return Release.from_dict(data.get("release") or data)

    # --- artists ---

    def get_artist(self, handle: str) -> ArtistProfileResult:
        """Return an artist's profile plus their latest tracks and releases."""
        return ArtistProfileResult.from_dict(self._get(f"/artists/{handle}"))

    # --- playlists ---

    def list_playlists(
        self,
        *,
        q: str | None = None,
        limit: int = _DEFAULT_LIMIT,
    ) -> PlaylistListResult:
        """List public playlists, optionally filtered by ``q``."""
        return PlaylistListResult.from_dict(self._get("/playlists", {"q": q, "limit": limit}))

    def get_playlist(self, playlist_id: str) -> Playlist:
        """Return a single public playlist by ID."""
        data = self._get(f"/playlists/{playlist_id}")
        return Playlist.from_dict(data.get("playlist") or data)

    def __repr__(self) -> str:
        masked = f"{self._token[:8]}{'*' * max(0, len(self._token) - 8)}"
        return f"SoundviaClient(token={masked!r}, base_url={self._base_url!r})"

    def __enter__(self) -> "SoundviaClient":
        return self

    def __exit__(self, *_: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# OAuth helper – build the authorization URL
# ---------------------------------------------------------------------------

def build_authorization_url(
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str = "",
    *,
    base_url: str = _OAUTH_BASE_URL,
) -> str:
    """
    Return the URL to redirect users to for OAuth authorization.

    Supported scopes:
        user.read, user.email, library.read, library.write,
        playlists.read, playlists.write, listening.read,
        follows.read, follows.write, notifications.read,
        playback.control, comments.write

    Example::

        url = build_authorization_url(
            client_id="svcli_...",
            redirect_uri="https://myapp.com/callback",
            scope="user.read library.read playlists.write",
            state="random_csrf_token",
        )
        # redirect the user's browser to `url`
    """
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
    }
    if state:
        params["state"] = state
    return f"{base_url.rstrip('/')}/oauth/authorize?{urllib.parse.urlencode(params)}"


# ---------------------------------------------------------------------------
# OAuth client  (user access token)
# ---------------------------------------------------------------------------

class OAuthClient(_HttpMixin):
    """
    Client for the Soundvia OAuth user API (``/oauth/api/*`` and ``/oauth/*``).

    Typically obtained via :meth:`OAuthClient.from_code` or
    :meth:`OAuthClient.from_token`::

        # exchange an authorization code
        client = OAuthClient.from_code(
            client_id="svcli_...",
            client_secret="svsec_...",
            code=request.args["code"],
            redirect_uri="https://myapp.com/callback",
        )

        # or supply an existing access token directly
        client = OAuthClient.from_token("svtok_...")
    """

    def __init__(
        self,
        token: OAuthToken | None = None,
        *,
        client_id: str = "",
        client_secret: str = "",
        base_url: str = _OAUTH_BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ) -> None:
        self._token_obj = token
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

    # --- constructors ---

    @classmethod
    def from_code(
        cls,
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str,
        *,
        base_url: str = _OAUTH_BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ) -> "OAuthClient":
        """Exchange an authorization ``code`` for an access token."""
        instance = cls(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        instance._token_obj = instance._exchange_code(code, redirect_uri)
        return instance

    @classmethod
    def from_token(
        cls,
        access_token: str,
        *,
        client_id: str = "",
        client_secret: str = "",
        refresh_token: str = "",
        base_url: str = _OAUTH_BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ) -> "OAuthClient":
        """Create a client from an already-obtained access token string."""
        token_obj = OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            expires_in=3600,
            refresh_token=refresh_token,
            scope="",
            raw={},
        )
        return cls(
            token=token_obj,
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

    # --- token management ---

    @property
    def token(self) -> OAuthToken | None:
        """The current :class:`OAuthToken`, or ``None`` if not yet set."""
        return self._token_obj

    def _token_endpoint_headers(self) -> dict[str, str]:
        """Headers for /oauth/token and /oauth/revoke — no Bearer needed."""
        return {
            "Accept": "application/json",
            "User-Agent": "soundvia-python/2.0.0",
        }

    def _exchange_code(self, code: str, redirect_uri: str) -> OAuthToken:
        url = f"{self._base_url}/oauth/token"
        body = json.dumps({
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }).encode("utf-8")
        headers = self._token_endpoint_headers()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        attempt = 0
        while True:
            attempt += 1
            try:
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    return OAuthToken.from_dict(json.loads(resp.read().decode("utf-8")))
            except urllib.error.HTTPError as exc:
                raw = ""
                try:
                    raw = exc.read().decode("utf-8")
                except Exception:
                    pass
                if exc.code >= 500 and attempt <= self._max_retries:
                    time.sleep(2 ** attempt)
                    continue
                try:
                    msg = json.loads(raw).get("error_description") or json.loads(raw).get("error", str(exc))
                except Exception:
                    msg = str(exc)
                raise APIError(msg, status_code=exc.code) from exc
            except urllib.error.URLError as exc:
                if attempt <= self._max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise APIError(f"Network error: {exc.reason}") from exc

    def refresh(self) -> OAuthToken:
        """
        Use the stored refresh token to obtain a new access token.

        The client's internal token is updated in place and also returned.
        """
        if not self._token_obj or not self._token_obj.refresh_token:
            raise APIError("No refresh token available.")
        url = f"{self._base_url}/oauth/token"
        body = json.dumps({
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": self._token_obj.refresh_token,
        }).encode("utf-8")
        headers = self._token_endpoint_headers()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        attempt = 0
        while True:
            attempt += 1
            try:
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    self._token_obj = OAuthToken.from_dict(json.loads(resp.read().decode("utf-8")))
                    return self._token_obj
            except urllib.error.HTTPError as exc:
                if exc.code >= 500 and attempt <= self._max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise APIError(str(exc), status_code=exc.code) from exc
            except urllib.error.URLError as exc:
                if attempt <= self._max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise APIError(f"Network error: {exc.reason}") from exc

    def revoke(self) -> bool:
        """Revoke the current access (and refresh) token. Returns ``True`` on success."""
        if not self._token_obj:
            return False
        url = f"{self._base_url}/oauth/revoke"
        body = json.dumps({"token": self._token_obj.access_token}).encode("utf-8")
        headers = self._token_endpoint_headers()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return bool(data.get("revoked", False))
        except Exception:
            return False

    def token_info(self) -> dict:
        """Return raw token metadata from ``/oauth/tokeninfo``."""
        return self._get_oauth("/oauth/tokeninfo")

    # --- internal HTTP helpers ---

    def _headers(self) -> dict[str, str]:
        if not self._token_obj or not self._token_obj.access_token:
            raise AuthenticationError("No access token set on OAuthClient.")
        return {
            "Authorization": f"Bearer {self._token_obj.access_token}",
            "Accept": "application/json",
            "User-Agent": "soundvia-python/2.0.0",
        }

    def _get_oauth(self, path: str, params: dict | None = None) -> dict:
        url = self._build_url(self._base_url, path, params)
        return self._request("GET", url)

    def _post_oauth(self, path: str, body: dict | None = None) -> dict:
        url = self._build_url(self._base_url, path)
        return self._request("POST", url, body)

    def _delete_oauth(self, path: str, body: dict | None = None) -> dict:
        url = self._build_url(self._base_url, path)
        return self._request("DELETE", url, body)

    # --- OAuth user API ---

    def me(self) -> UserProfile:
        """
        Return the authenticated user's profile.

        Requires scope: ``user.read``
        """
        data = self._get_oauth("/oauth/api/me")
        return UserProfile.from_dict(data.get("user") or data)

    def get_library(self) -> LibraryResult:
        """
        Return the user's unified library (playlists, releases, presaves).

        Requires scope: ``library.read``
        """
        return LibraryResult.from_dict(self._get_oauth("/oauth/api/library"))

    def save_to_library(self, item_type: str, item_id: str) -> bool:
        """
        Save a release, playlist, or presave to the user's library.

        ``item_type`` must be ``"release"``, ``"playlist"``, or ``"presave_release"``.

        Requires scope: ``library.write``
        """
        data = self._post_oauth("/oauth/api/library/save", {"type": item_type, "id": item_id})
        return bool(data.get("saved", False))

    def remove_from_library(self, item_type: str, item_id: str) -> bool:
        """
        Remove a release, playlist, or presave from the user's library.

        ``item_type`` must be ``"release"``, ``"playlist"``, or ``"presave_release"``.

        Requires scope: ``library.write``
        """
        data = self._post_oauth("/oauth/api/library/remove", {"type": item_type, "id": item_id})
        return bool(data.get("removed", False))

    def get_playlists(self) -> UserPlaylistListResult:
        """
        Return playlists owned or followed by the user.

        Requires scope: ``playlists.read``
        """
        return UserPlaylistListResult.from_dict(self._get_oauth("/oauth/api/playlists"))

    def create_playlist(self, name: str, *, description: str = "") -> UserPlaylist:
        """
        Create a new playlist on behalf of the user.

        Requires scope: ``playlists.write``
        """
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        data = self._post_oauth("/oauth/api/playlists", body)
        return UserPlaylist.from_dict(data.get("playlist") or data)

    def add_track_to_playlist(self, playlist_id: str, track_id: str) -> bool:
        """
        Add a track to one of the user's playlists.

        Requires scope: ``playlists.write``
        """
        data = self._post_oauth(
            f"/oauth/api/playlists/{playlist_id}/tracks",
            {"track_id": track_id},
        )
        return bool(data.get("added", False))

    def remove_track_from_playlist(self, playlist_id: str, track_id: str) -> bool:
        """
        Remove a track from one of the user's playlists.

        Requires scope: ``playlists.write``
        """
        data = self._delete_oauth(
            f"/oauth/api/playlists/{playlist_id}/tracks",
            {"track_id": track_id},
        )
        return bool(data.get("removed", False))

    def get_listening_history(self) -> PlayHistoryResult:
        """
        Return the user's recent play history (up to 100 entries).

        Requires scope: ``listening.read``
        """
        return PlayHistoryResult.from_dict(self._get_oauth("/oauth/api/history"))

    def get_follows(self) -> FollowsResult:
        """
        Return IDs of users the authenticated user follows.

        Requires scope: ``follows.read``
        """
        return FollowsResult.from_dict(self._get_oauth("/oauth/api/follows"))

    def follow(self, user_id: str) -> bool:
        """
        Follow a user on behalf of the authenticated user.

        Requires scope: ``follows.write``
        """
        data = self._post_oauth("/oauth/api/follows", {"user_id": user_id})
        return bool(data.get("followed", False))

    def unfollow(self, user_id: str) -> bool:
        """
        Unfollow a user on behalf of the authenticated user.

        Requires scope: ``follows.write``
        """
        data = self._delete_oauth("/oauth/api/follows", {"user_id": user_id})
        return bool(data.get("unfollowed", False))

    def get_notifications(self) -> NotificationsResult:
        """
        Return the user's recent notifications (up to 50 entries).

        Requires scope: ``notifications.read``
        """
        return NotificationsResult.from_dict(self._get_oauth("/oauth/api/notifications"))

    def post_comment(self, track_id: str, text: str) -> str:
        """
        Post a comment on a track. Returns the new comment ID.

        Requires scope: ``comments.write``
        """
        data = self._post_oauth("/oauth/api/comments", {"track_id": track_id, "text": text})
        return str(data.get("comment_id", ""))

    def __repr__(self) -> str:
        tok = self._token_obj.access_token if self._token_obj else ""
        masked = f"{tok[:10]}***" if tok else "(no token)"
        return f"OAuthClient(token={masked!r}, base_url={self._base_url!r})"

    def __enter__(self) -> "OAuthClient":
        return self

    def __exit__(self, *_: Any) -> None:
        pass
