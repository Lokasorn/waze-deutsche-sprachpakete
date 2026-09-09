import urllib.request
import json
import ssl
import os

ctx = ssl._create_unverified_context()
out_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples"
os.makedirs(out_dir, exist_ok=True)

# Search specifically for Rubble Hörspiele
queries = [
    "paw patrol rubble der fundhund",
    "rubble und crew repariert eine straße"
]

all_tracks = []
for q in queries:
    url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
        for track in data.get('data', []):
            preview = track.get('preview')
            title = track.get('title')
            album = track.get('album', {}).get('title')
            if preview:
                all_tracks.append((title, album, preview))

print(f"Found {len(all_tracks)} tracks with preview.")

for i, (title, album, preview) in enumerate(all_tracks[:15]):
    safe_name = "".join(c for c in f"{album}_{title}" if c.isalnum() or c in " _-")[:60]
    filename = os.path.join(out_dir, f"{i:02d}_{safe_name}.mp3")
    if not os.path.exists(filename):
        try:
            req = urllib.request.Request(preview, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx) as r, open(filename, 'wb') as f:
                f.write(r.read())
            print(f"Downloaded: {filename} ({os.path.getsize(filename)} bytes)")
        except Exception as e:
            print(f"Failed {filename}: {e}")
    else:
        print(f"Already exists: {filename}")
