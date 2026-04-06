from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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


@dataclass
class SearchResult:
    tracks: list[dict]
    releases: list[dict]
    artists: list[dict]
    playlists: list[dict]
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "SearchResult":
        return cls(
            tracks=data.get("tracks", []),
            releases=data.get("releases", []),
            artists=data.get("artists", []),
            playlists=data.get("playlists", []),
            raw=data,
        )


@dataclass
class Track:
    id: str
    title: str
    duration: int | None
    stream_url: str | None
    cover_url: str | None
    artist_id: str | None
    artist_handle: str | None
    release_id: str | None
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Track":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            duration=data.get("duration"),
            stream_url=data.get("stream_url"),
            cover_url=data.get("cover_url"),
            artist_id=data.get("artist_id"),
            artist_handle=data.get("artist_handle"),
            release_id=data.get("release_id"),
            created_at=data.get("created_at"),
            raw=data,
        )


@dataclass
class TrackListResult:
    tracks: list[Track]
    total: int | None
    limit: int | None
    offset: int | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "TrackListResult":
        return cls(
            tracks=[Track.from_dict(t) for t in data.get("tracks", [])],
            total=data.get("total"),
            limit=data.get("limit"),
            offset=data.get("offset"),
            raw=data,
        )


@dataclass
class Release:
    id: str
    title: str
    release_type: str | None
    cover_url: str | None
    artist_id: str | None
    artist_handle: str | None
    tracks: list[Track]
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Release":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            release_type=data.get("type") or data.get("release_type"),
            cover_url=data.get("cover_url"),
            artist_id=data.get("artist_id"),
            artist_handle=data.get("artist_handle"),
            tracks=[Track.from_dict(t) for t in data.get("tracks", [])],
            created_at=data.get("created_at"),
            raw=data,
        )


@dataclass
class ReleaseListResult:
    releases: list[Release]
    total: int | None
    limit: int | None
    offset: int | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "ReleaseListResult":
        return cls(
            releases=[Release.from_dict(r) for r in data.get("releases", [])],
            total=data.get("total"),
            limit=data.get("limit"),
            offset=data.get("offset"),
            raw=data,
        )


@dataclass
class Artist:
    id: str
    handle: str
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    follower_count: int | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Artist":
        return cls(
            id=data.get("id", ""),
            handle=data.get("handle", ""),
            display_name=data.get("display_name"),
            bio=data.get("bio"),
            avatar_url=data.get("avatar_url"),
            follower_count=data.get("follower_count"),
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


@dataclass
class Playlist:
    id: str
    title: str
    owner_id: str | None
    owner_handle: str | None
    cover_url: str | None
    track_count: int | None
    tracks: list[Track]
    created_at: str | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Playlist":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            owner_id=data.get("owner_id") or data.get("user_id"),
            owner_handle=data.get("owner_handle"),
            cover_url=data.get("cover_url"),
            track_count=data.get("track_count"),
            tracks=[Track.from_dict(t) for t in data.get("tracks", [])],
            created_at=data.get("created_at"),
            raw=data,
        )


@dataclass
class PlaylistListResult:
    playlists: list[Playlist]
    total: int | None
    limit: int | None
    offset: int | None
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "PlaylistListResult":
        return cls(
            playlists=[Playlist.from_dict(p) for p in data.get("playlists", [])],
            total=data.get("total"),
            limit=data.get("limit"),
            offset=data.get("offset"),
            raw=data,
        )
