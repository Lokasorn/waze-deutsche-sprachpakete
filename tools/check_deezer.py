import urllib.request
import json
import ssl

ctx = ssl._create_unverified_context()

queries = [
    "paw patrol rubble deutsch",
    "paw patrol rubble",
    "paw patrol folge",
    "paw patrol mutige welpen",
    "rubble und crew"
]

for q in queries:
    url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            print(f"=== Query: {q} (Total: {data.get('total')}) ===")
            for track in data.get('data', [])[:5]:
                print(f"Title: {track.get('title')} | Artist: {track.get('artist', {}).get('name')}")
                print(f"Album: {track.get('album', {}).get('title')}")
                print(f"Preview MP3: {track.get('preview')}")
                print("-" * 40)
    except Exception as e:
        print(f"Err for {q}: {e}")
