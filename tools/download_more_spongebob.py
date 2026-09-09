import urllib.request
import json
import ssl
import urllib.parse
import os

ctx = ssl._create_unverified_context()
out_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples_more"
os.makedirs(out_dir, exist_ok=True)

queries = [
    "spongebob folge",
    "folge das original hoerspiel zur tv serie",
    "spongebob karatefieber",
    "spongebob hosen"
]

all_tracks = {}

for q in queries:
    u = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}&limit=30"
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            d = json.loads(r.read().decode())
            for item in d.get('data', []):
                album_title = item.get('album', {}).get('title', '')
                track_title = item.get('title', '')
                preview = item.get('preview')
                if 'Original-Hörspiel' in album_title or 'Folge' in album_title or 'SpongeBob' in album_title:
                    if preview and preview not in all_tracks:
                        all_tracks[preview] = {
                            'title': track_title,
                            'album': album_title,
                            'preview': preview
                        }
    except Exception as e:
        print(f"Error {q}: {e}")

print(f"Found {len(all_tracks)} relevant tracks!")
for i, (prev, meta) in enumerate(list(all_tracks.items())[:20]):
    print(f"{i:02d}: {meta['album']} - {meta['title']}")
    # Download preview
    fname = f"{i:02d}_{meta['album'][:20]}_{meta['title'][:20]}.mp3".replace('/', '_').replace('\\', '_').replace(':', '_').replace(' ', '_')
    fpath = os.path.join(out_dir, fname)
    if not os.path.exists(fpath):
        try:
            urllib.request.urlretrieve(prev, fpath)
        except Exception as err:
            print(f"  Failed download: {err}")

print("Previews downloaded!")
