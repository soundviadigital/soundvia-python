__version__ = "1.0.0"
__author__ = "soundvia"

from .client import SoundviaClient
from .models import (
    AppInfo,
    AppLimits,
    Artist,
    ArtistProfileResult,
    Playlist,
    PlaylistListResult,
    Release,
    ReleaseListResult,
    SearchResult,
    StatusResult,
    Track,
    TrackListResult,
)
from .exceptions import (
    SoundviaError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError,
)

__all__ = [
    "SoundviaClient",
    "AppInfo",
    "AppLimits",
    "Artist",
    "ArtistProfileResult",
    "Playlist",
    "PlaylistListResult",
    "Release",
    "ReleaseListResult",
    "SearchResult",
    "StatusResult",
    "Track",
    "TrackListResult",
    "SoundviaError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "APIError",
]
