# soundvia

Python client for the [soundvia.eu](https://soundvia.eu) API v1

## Installation

```bash
pip install soundvia
```

```manual install
git clone https://github.com/soundviadigital/soundvia-python
cd soundvia-python
pip install .
```

## Usage

Get a token from your app page on soundvia.eu/developer, then pass it to the client.

```python
from soundvia import SoundviaClient

client = SoundviaClient("YOUR_APP_TOKEN")
```

**Status** — check your app info and current rate limit config:

```python
status = client.status()
print(status.app.name)
print(status.app.verification_status)  # "pending" or "verified"
print(status.app.limits.requests_per_minute)
```

**Search** — searches across tracks, releases, artists, and playlists at once:

```python
results = client.search("lofi beats")
for track in results.tracks:
    print(track["title"])
```

**Tracks:**

```python
page = client.list_tracks(q="chill", limit=10)
for track in page.tracks:
    print(track.title, track.duration)

track = client.get_track("TRACK_ID")
print(track.stream_url)
```

**Releases:**

```python
page = client.list_releases(q="ep", limit=5)
release = client.get_release("RELEASE_ID")
print(release.release_type)  # "album", "ep", "single"
```

**Artists:**

```python
profile = client.get_artist("rebzyyx")
print(profile.artist.display_name)
for track in profile.tracks:
    print(track.title)
```

**Playlists:**

```python
page = client.list_playlists(q="woah")
playlist = client.get_playlist("PLAYLIST_ID")
```

**Pagination** — all `list_*` methods take `limit` (default `20`) and `offset`:

```python
page1 = client.list_tracks(q="jazz", limit=20, offset=0)
page2 = client.list_tracks(q="jazz", limit=20, offset=20)
```

**Context manager:**

```python
with SoundviaClient("YOUR_APP_TOKEN") as client:
    print(client.status().app.name)
```

## Client options

```python
SoundviaClient(
    token,
    base_url="https://soundvia.eu/api/v1",
    timeout=15,       # seconds
    max_retries=3,    # retries on 429 and 5xx
)
```

On a 429, the client reads the `Retry-After` header and sleeps before retrying. On 5xx errors it backs off exponentially. Both give up after `max_retries` attempts.

## Errors

```python
from soundvia import AuthenticationError, NotFoundError, RateLimitError, APIError

try:
    track = client.get_track("bad-id")
except NotFoundError:
    print("track doesn't exist")
except RateLimitError as e:
    print(f"retry after {e.retry_after}s")
except AuthenticationError:
    print("check your token")
except APIError as e:
    print(e.status_code)
```

All exceptions inherit from `SoundviaError`.

| Exception | Trigger |
|---|---|
| `AuthenticationError` | 401 |
| `NotFoundError` | 404 |
| `RateLimitError` | 429 (after retries exhausted) |
| `APIError` | 5xx or network failure |

## Every response has a `.raw` field

If a field isn't modelled yet, the original response dict is always there:

```python
track = client.get_track("TRACK_ID")
print(track.raw)
```

## Tests

```bash
pip install pytest
pytest tests/
```

