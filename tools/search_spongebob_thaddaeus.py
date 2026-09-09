import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "7e8910080ae94576a91f52b0f4fa6e89"
headers = {"Authorization": f"Bearer {API_KEY}"}

queries = [
    "SpongeBob", "Spongebob Deutsch", "Santiago Ziesmer",
    "Thaddäus", "Thaddaeus", "Squidward", "Squidward German", "Thaddäus Tentakel"
]

for q in queries:
    url = f"https://api.fish.audio/model?title={urllib.parse.quote(q)}&page_size=20"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"=== Query: '{q}' (Total: {data.get('total', 0)}) ===")
            for item in data.get('items', [])[:8]:
                print(f"  {item.get('_id')} | {item.get('title')} | langs: {item.get('languages')}")
    except Exception as e:
        print(f"  Err for '{q}': {e}")
