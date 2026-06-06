# soundvia

Python client for the [soundvia.eu](https://soundvia.eu) API

## Installation

```bash
pip install soundvia
```

Or from source:
```bash
git clone https://github.com/soundviadigital/soundvia-python
cd soundvia-python
pip install .
```

## Two clients

| Class | Token type | Use for |
|---|---|---|
| `SoundviaClient` | App token (`svapp_…`) | Public content, tracks, releases, artists, playlists, search |
| `OAuthClient` | User access token (`svtok_…`) | User specific data, library, playlists, history, follows, notifications, comments |

---

## SoundviaClient — public API

Get an app token from [soundvia.eu/developer](https://soundvia.eu/developer).

```python
from soundvia import SoundviaClient

client = SoundviaClient("svapp_...")
```

### Status

```python
status = client.status()
print(status.app.name)
print(status.app.tier)                      # "app" or "approved_app"
print(status.app.verification_status)      # "none" | "pending" | "approved" | "declined"
print(status.app.limits.requests_per_minute)
```

### Search

Searches tracks, releases, and artists in one call:

```python
results = client.search("lofi beats")
for track in results.tracks:
    print(track.title, track.artist_name, track.stream_count)
for release in results.releases:
    print(release.title, release.release_type)   # "single" | "ep" | "album"
for artist in results.artists:
    print(artist.handle, artist.display_name)
```

### Tracks

```python
page = client.list_tracks(q="chill", limit=10)
for track in page.tracks:
    print(track.title, track.genre, track.cover_art, track.stream_count)

track = client.get_track("TRACK_ID")
print(track.artist_name, track.artist_handle, track.release_id)
```

### Releases

```python
page = client.list_releases(q="ep", limit=5)
release = client.get_release("RELEASE_ID")
print(release.release_type)   # "album", "ep", "single"
print(release.track_ids)      # list of track ID strings
print(release.genre, release.cover_art)
```

### Artists

```python
profile = client.get_artist("rebzyyx")
print(profile.artist.display_name, profile.artist.bio, profile.artist.avatar)
for track in profile.tracks:
    print(track.title)
for release in profile.releases:
    print(release.title)
```

### Playlists

```python
page = client.list_playlists(q="woah", limit=20)
playlist = client.get_playlist("PLAYLIST_ID")
print(playlist.name, playlist.description, playlist.track_ids)
```

---

## OAuthClient (User API)

### Step 1: build the authorization URL

Redirect the user to this URL in their browser:

```python
from soundvia import build_authorization_url

url = build_authorization_url(
    client_id="svcli_...",
    redirect_uri="https://myapp.com/callback",
    scope="user.read library.read playlists.write",
    state="random_csrf_token",
)


**Available scopes:**

| Scope | Access |
|---|---|
| `user.read` | Username, display name, avatar, role |
| `user.email` | Email address |
| `library.read` | Saved releases, playlists, presaves |
| `library.write` | Save/remove library items |
| `playlists.read` | User's playlists |
| `playlists.write` | Create playlists, add/remove tracks |
| `listening.read` | Play history |
| `follows.read` | Following list |
| `follows.write` | Follow/unfollow users |
| `notifications.read` | Notification feed |
| `playback.control` | Control playback |
| `comments.write` | Post/delete comments |

### Step 2,  exchange the code for a token

When the user approves, they're redirected to your `redirect_uri` with a `code` param:

```python
from soundvia import OAuthClient

client = OAuthClient.from_code(
    client_id="svcli_...",
    client_secret="svsec_...",
    code=request.args["code"],
    redirect_uri="https://myapp.com/callback",
)

# persist these for later use:
print(client.token.access_token)
print(client.token.refresh_token)
print(client.token.expires_in)
print(client.token.scope)
```

### Restore a saved token

```python
client = OAuthClient.from_token(
    "svtok_...",
    refresh_token="svref_...",
    client_id="svcli_...",
    client_secret="svsec_...",
)
```

### Token lifecycle

```python
# refresh an expired access token (rotates both tokens)
new_token = client.refresh()
print(new_token.access_token, new_token.refresh_token)

# revoke the current token
client.revoke()

# inspect the current token
info = client.token_info()
```

### User profile

```python
me = client.me()          # requires user.read
print(me.username, me.display_name, me.avatar, me.role)

me = client.me()          # add user.email scope to also get:
print(me.email)
```

### Library

```python
library = client.get_library()    # requires library.read
print(library.counts.total, library.counts.saved_releases)

for item in library.items:
    print(item.item_type, item.name, item.track_count)
    # item_type: "playlist" | "release" | "presave_release"
    print(item.is_owner, item.is_collaborator, item.visibility)

# save / remove  — requires library.write
client.save_to_library("release", "RELEASE_ID")
client.save_to_library("playlist", "PLAYLIST_ID")
client.save_to_library("presave_release", "RELEASE_ID")

client.remove_from_library("release", "RELEASE_ID")
```

### Playlists

```python
result = client.get_playlists()    # requires playlists.read
for pl in result.playlists:
    print(pl.name, pl.track_count, pl.is_owner, pl.visibility)

# create — requires playlists.write
pl = client.create_playlist("Late Night Jams", description="vibes only")
print(pl.id)

# add / remove tracks — requires playlists.write
client.add_track_to_playlist("PLAYLIST_ID", "TRACK_ID")
client.remove_track_from_playlist("PLAYLIST_ID", "TRACK_ID")
```

### Listening history

```python
history = client.get_listening_history()    # requires listening.read
for entry in history.history:
    print(entry.track_id, entry.played_at)
```

### Follows

```python
follows = client.get_follows()    # requires follows.read
print(follows.following_ids)

client.follow("USER_ID")          # requires follows.write
client.unfollow("USER_ID")
```

### Notifications

```python
notifs = client.get_notifications()    # requires notifications.read
for n in notifs.notifications:
    print(n.type, n.message, n.read, n.created_at)
```

### Comments

```python
comment_id = client.post_comment("TRACK_ID", "great track!")   # requires comments.write
```

---

## Error handling

```python
from soundvia import (
    AuthenticationError,
    NotFoundError,
    InsufficientScopeError,
    RateLimitError,
    APIError,
)

try:
    track = client.get_track("bad-id")
except NotFoundError:
    print("track doesn't exist")
except InsufficientScopeError:
    print("token is missing a required scope")
except RateLimitError as e:
    print(f"retry after {e.retry_after}s")
except AuthenticationError:
    print("check your token")
except APIError as e:
    print(e.status_code)
```

All exceptions inherit from `SoundviaError`.

| Exception | HTTP status |
|---|---|
| `AuthenticationError` | 401 |
| `InsufficientScopeError` | 403 |
| `NotFoundError` | 404 |
| `RateLimitError` | 429 (after retries) |
| `APIError` | 5xx or network failure |

On 429 the client reads `Retry-After` and sleeps before retrying. On 5xx it backs off exponentially. Both give up after `max_retries` attempts (default 3).

## Every response has a `.raw` field

```python
track = client.get_track("TRACK_ID")
print(track.raw)   # original response dict
```

## Client options

```python
SoundviaClient(
    token,
    base_url="https://soundvia.eu/api/v1",
    timeout=15,
    max_retries=3,
)

OAuthClient.from_token(
    access_token,
    client_id="",
    client_secret="",
    refresh_token="",
    base_url="https://soundvia.eu",
    timeout=15,
    max_retries=3,
)
```

## Context manager

```python
with SoundviaClient("svapp_...") as client:
    print(client.status().app.name)

with OAuthClient.from_token("svtok_...") as client:
    print(client.me().username)
```

## Tests

```bash
pip install pytest
pytest tests/
```
