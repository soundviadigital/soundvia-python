__version__ = "2.0.0"
__author__ = "soundvia"

from .client import SoundviaClient, OAuthClient, build_authorization_url
from .models import (
    # app / status
    AppInfo,
    AppLimits,
    StatusResult,
    # public content
    Track,
    TrackListResult,
    Release,
    ReleaseListResult,
    Artist,
    ArtistProfileResult,
    Playlist,
    PlaylistListResult,
    SearchResult,
    # OAuth / user
    OAuthToken,
    UserProfile,
    LibraryItem,
    LibraryCounts,
    LibraryResult,
    UserPlaylist,
    UserPlaylistListResult,
    PlayHistoryEntry,
    PlayHistoryResult,
    FollowsResult,
    Notification,
    NotificationsResult,
)
from .exceptions import (
    SoundviaError,
    AuthenticationError,
    NotFoundError,
    InsufficientScopeError,
    RateLimitError,
    APIError,
)

__all__ = [
    # clients
    "SoundviaClient",
    "OAuthClient",
    "build_authorization_url",
    # app / status
    "AppInfo",
    "AppLimits",
    "StatusResult",
    # public content
    "Track",
    "TrackListResult",
    "Release",
    "ReleaseListResult",
    "Artist",
    "ArtistProfileResult",
    "Playlist",
    "PlaylistListResult",
    "SearchResult",
    # OAuth / user
    "OAuthToken",
    "UserProfile",
    "LibraryItem",
    "LibraryCounts",
    "LibraryResult",
    "UserPlaylist",
    "UserPlaylistListResult",
    "PlayHistoryEntry",
    "PlayHistoryResult",
    "FollowsResult",
    "Notification",
    "NotificationsResult",
    # exceptions
    "SoundviaError",
    "AuthenticationError",
    "NotFoundError",
    "InsufficientScopeError",
    "RateLimitError",
    "APIError",
]
