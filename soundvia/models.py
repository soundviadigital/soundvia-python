from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# App / Status
# ---------------------------------------------------------------------------

@dataclass
class AppLimits:
    requests_per_minute: int
    response_bytes_per_minute: int

    @classmethod
    def from_dict(cls, data: dict) -> "AppLimits":
        return cls(
            requests_per_minute=data.get("requests_per_minute", 0),
            response_bytes_per_minute=data.get("response_bytes_per_minute", 0),
        )


@dataclass
class AppInfo:
    id: str
    name: str
    tier: str
    verification_status: str
    limits: AppLimits

    @classmethod
    def from_dict(cls, data: dict) -> "AppInfo":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            tier=data.get("tier", ""),
            verification_status=data.get("verification_status", ""),
            limits=AppLimits.from_dict(data.get("limits", {})),
        )


@dataclass
class StatusResult:
    ok: bool
    api: str
    app: AppInfo
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "StatusResult":
        return cls(
            ok=data.get("ok", False),
            api=data.get("api", ""),
            app=AppInfo.from_dict(data.get("app", {})),
            raw=data,
        )


# ---------------------------------------------------------------------------
# Track
# ---------------------------------------------------------------------------

@dataclass
class Track:
    id: str
    title: str
    artist_id: str | None
    artist_name: str | None
    artist_handle: str | None
    genre: str | None
    cover_art: str | None
    stream_count: int
    release_id: str | None
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Track":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            artist_id=data.get("artist_id") or None,
            artist_name=data.get("artist_name") or None,
            artist_handle=data.get("artist_handle") or None,
            genre=data.get("genre") or None,
            cover_art=data.get("cover_art") or None,
            stream_count=int(data.get("stream_count", 0) or 0),
            release_id=data.get("release_id") or None,
            created_at=data.get("created_at") or None,
            raw=data,
        )


@dataclass
class TrackListResult:
    tracks: list[Track]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "TrackListResult":
        return cls(
            tracks=[Track.from_dict(t) for t in data.get("tracks", [])],
            raw=data,
        )


# ---------------------------------------------------------------------------
# Release
# ---------------------------------------------------------------------------

@dataclass
class Release:
    id: str
    title: str
    release_type: str | None
    artist_id: str | None
    artist_name: str | None
    artist_handle: str | None
    genre: str | None
    cover_art: str | None
    track_ids: list[str]
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Release":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            release_type=data.get("release_type") or data.get("type") or None,
            artist_id=data.get("artist_id") or None,
            artist_name=data.get("artist_name") or None,
            artist_handle=data.get("artist_handle") or None,
            genre=data.get("genre") or None,
            cover_art=data.get("cover_art") or None,
            track_ids=[str(t) for t in (data.get("track_ids") or data.get("tracks") or [])],
            created_at=data.get("created_at") or None,
            raw=data,
        )


@dataclass
class ReleaseListResult:
    releases: list[Release]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "ReleaseListResult":
        return cls(
            releases=[Release.from_dict(r) for r in data.get("releases", [])],
            raw=data,
        )


# ---------------------------------------------------------------------------
# Artist
# ---------------------------------------------------------------------------

@dataclass
class Artist:
    id: str
    handle: str
    display_name: str | None
    avatar: str | None
    bio: str | None
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Artist":
        return cls(
            id=data.get("id", ""),
            handle=data.get("handle", ""),
            display_name=data.get("display_name") or None,
            avatar=data.get("avatar") or None,
            bio=data.get("bio") or None,
            created_at=data.get("created_at") or None,
            raw=data,
        )


@dataclass
class ArtistProfileResult:
    artist: Artist
    tracks: list[Track]
    releases: list[Release]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "ArtistProfileResult":
        return cls(
            artist=Artist.from_dict(data.get("artist", {})),
            tracks=[Track.from_dict(t) for t in data.get("tracks", [])],
            releases=[Release.from_dict(r) for r in data.get("releases", [])],
            raw=data,
        )


# ---------------------------------------------------------------------------
# Playlist
# ---------------------------------------------------------------------------

@dataclass
class Playlist:
    id: str
    name: str
    description: str | None
    cover_art: str | None
    track_ids: list[str]
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Playlist":
        return cls(
            id=data.get("id", ""),
            name=data.get("name") or data.get("title", ""),
            description=data.get("description") or None,
            cover_art=data.get("cover_art") or None,
            track_ids=[str(t) for t in (data.get("track_ids") or data.get("tracks") or [])],
            created_at=data.get("created_at") or None,
            raw=data,
        )


@dataclass
class PlaylistListResult:
    playlists: list[Playlist]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "PlaylistListResult":
        return cls(
            playlists=[Playlist.from_dict(p) for p in data.get("playlists", [])],
            raw=data,
        )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@dataclass
class SearchResult:
    query: str
    tracks: list[Track]
    releases: list[Release]
    artists: list[Artist]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "SearchResult":
        return cls(
            query=data.get("query", ""),
            tracks=[Track.from_dict(t) for t in data.get("tracks", [])],
            releases=[Release.from_dict(r) for r in data.get("releases", [])],
            artists=[Artist.from_dict(a) for a in data.get("artists", [])],
            raw=data,
        )


# ---------------------------------------------------------------------------
# OAuth – token
# ---------------------------------------------------------------------------

@dataclass
class OAuthToken:
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "OAuthToken":
        return cls(
            access_token=data.get("access_token", ""),
            token_type=data.get("token_type", "Bearer"),
            expires_in=int(data.get("expires_in", 3600) or 3600),
            refresh_token=data.get("refresh_token", ""),
            scope=data.get("scope", ""),
            raw=data,
        )


# ---------------------------------------------------------------------------
# OAuth – user profile (/oauth/api/me)
# ---------------------------------------------------------------------------

@dataclass
class UserProfile:
    id: str
    username: str | None
    display_name: str | None
    avatar: str | None
    role: str | None
    email: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        return cls(
            id=data.get("id", ""),
            username=data.get("username") or None,
            display_name=data.get("display_name") or None,
            avatar=data.get("avatar") or None,
            role=data.get("role") or None,
            email=data.get("email") or None,
            raw=data,
        )


# ---------------------------------------------------------------------------
# OAuth – library (/oauth/api/library)
# ---------------------------------------------------------------------------

@dataclass
class LibraryItem:
    library_key: str
    item_type: str           # "playlist" | "release" | "presave_release"
    item_id: str
    name: str
    description: str | None
    cover_art: str | None
    href: str | None
    track_count: int
    is_saved_item: bool
    is_owner: bool | None
    is_collaborator: bool | None
    visibility: str | None
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryItem":
        return cls(
            library_key=data.get("library_key", ""),
            item_type=data.get("item_type", ""),
            item_id=data.get("item_id", ""),
            name=data.get("name", ""),
            description=data.get("description") or None,
            cover_art=data.get("cover_art") or None,
            href=data.get("href") or None,
            track_count=int(data.get("track_count", 0) or 0),
            is_saved_item=bool(data.get("is_saved_item", False)),
            is_owner=data.get("is_owner"),
            is_collaborator=data.get("is_collaborator"),
            visibility=data.get("visibility") or None,
            created_at=data.get("created_at") or None,
            raw=data,
        )


@dataclass
class LibraryCounts:
    total: int
    saved_releases: int
    saved_playlists: int
    presaved_releases: int

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryCounts":
        return cls(
            total=int(data.get("total", 0) or 0),
            saved_releases=int(data.get("saved_releases", 0) or 0),
            saved_playlists=int(data.get("saved_playlists", 0) or 0),
            presaved_releases=int(data.get("presaved_releases", 0) or 0),
        )


@dataclass
class LibraryResult:
    items: list[LibraryItem]
    counts: LibraryCounts
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryResult":
        items_data = data.get("library") or data.get("items") or []
        return cls(
            items=[LibraryItem.from_dict(i) for i in items_data],
            counts=LibraryCounts.from_dict(data.get("counts", {})),
            raw=data,
        )


# ---------------------------------------------------------------------------
# OAuth – user playlists (/oauth/api/playlists)
# ---------------------------------------------------------------------------

@dataclass
class UserPlaylist:
    id: str
    name: str
    description: str | None
    cover_art: str | None
    track_count: int
    is_owner: bool
    visibility: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "UserPlaylist":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description") or None,
            cover_art=data.get("cover_art") or None,
            track_count=int(data.get("track_count", 0) or 0),
            is_owner=bool(data.get("is_owner", False)),
            visibility=data.get("visibility") or None,
            raw=data,
        )


@dataclass
class UserPlaylistListResult:
    playlists: list[UserPlaylist]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "UserPlaylistListResult":
        return cls(
            playlists=[UserPlaylist.from_dict(p) for p in data.get("playlists", [])],
            raw=data,
        )


# ---------------------------------------------------------------------------
# OAuth – listening history (/oauth/api/history)
# ---------------------------------------------------------------------------

@dataclass
class PlayHistoryEntry:
    track_id: str
    played_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "PlayHistoryEntry":
        return cls(
            track_id=data.get("track_id", ""),
            played_at=data.get("played_at") or None,
            raw=data,
        )


@dataclass
class PlayHistoryResult:
    history: list[PlayHistoryEntry]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "PlayHistoryResult":
        return cls(
            history=[PlayHistoryEntry.from_dict(e) for e in data.get("history", [])],
            raw=data,
        )


# ---------------------------------------------------------------------------
# OAuth – follows (/oauth/api/follows)
# ---------------------------------------------------------------------------

@dataclass
class FollowsResult:
    following_ids: list[str]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "FollowsResult":
        return cls(
            following_ids=[str(i) for i in data.get("following_ids", [])],
            raw=data,
        )


# ---------------------------------------------------------------------------
# OAuth – notifications (/oauth/api/notifications)
# ---------------------------------------------------------------------------

@dataclass
class Notification:
    id: str
    type: str | None
    message: str | None
    read: bool
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        return cls(
            id=data.get("id", ""),
            type=data.get("type") or None,
            message=data.get("message") or None,
            read=bool(data.get("read", False)),
            created_at=data.get("created_at") or None,
            raw=data,
        )


@dataclass
class NotificationsResult:
    notifications: list[Notification]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationsResult":
        return cls(
            notifications=[Notification.from_dict(n) for n in data.get("notifications", [])],
            raw=data,
        )