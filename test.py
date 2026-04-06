from soundvia import SoundviaClient

client = SoundviaClient("your_api_key_here")

# Check what came back in the search
results = client.search("one more time")
print("Tracks found:", results.tracks)
print("Artists found:", results.artists)
print("Releases found:", results.releases)
print("Playlists found:", results.playlists)