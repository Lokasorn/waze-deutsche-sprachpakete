import urllib.request
import json
import ssl

ctx = ssl._create_unverified_context()
queries = [
    "spongebob fahrschule",
    "spongebob bootsfahrschule",
    "spongebob quallenjagd",
    "spongebob blubberbernd",
    "spongebob seepferdchen"
]

for q in queries:
    url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            d = json.loads(resp.read().decode())
            print(f"=== {q} (Total: {d.get('total', 0)}) ===")
            for t in d.get('data', [])[:3]:
                print(f"  {t.get('title')} | {t.get('album', {}).get('title')} | {t.get('preview')}")
    except Exception as e:
        print(f"Err {q}: {e}")
