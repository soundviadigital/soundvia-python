from soundvia import SoundviaClient, NotFoundError, RateLimitError, APIError

APP_TOKEN = "token_here"

client = SoundviaClient(APP_TOKEN)

# status()
status = client.status()
print("status:", status)

# search()
search = client.search("one more time", limit=5)
print("search tracks:", search.tracks)
print("search releases:", search.releases)
print("search artists:", search.artists)

# list_tracks()
tracks = client.list_tracks(limit=5)
print("list_tracks:", tracks.tracks)

# get_track()
if tracks.tracks:
    track = client.get_track(tracks.tracks[0].id)
    print("get_track:", track)

# list_releases()
releases = client.list_releases(limit=5)
print("list_releases:", releases.releases)

# get_release()
if releases.releases:
    release = client.get_release(releases.releases[0].id)
    print("get_release:", release)

# get_artist()
if search.artists:
    artist = client.get_artist(search.artists[0].handle)
    print("get_artist:", artist)

# list_playlists()
playlists = client.list_playlists(limit=5)
print("list_playlists:", playlists.playlists)

# get_playlist()
if playlists.playlists:
    playlist = client.get_playlist(playlists.playlists[0].id)
    print("get_playlist:", playlist)

# NotFoundError
try:
    client.get_track("000000000000000000000000")
except NotFoundError as e:
    print("NotFoundError:", e)

# RateLimitError
try:
    raise RateLimitError(retry_after=30)
except RateLimitError as e:
    print("RateLimitError retry_after:", e.retry_after)

# APIError
try:
    raise APIError("something broke", status_code=503)
except APIError as e:
    print("APIError status_code:", e.status_code)