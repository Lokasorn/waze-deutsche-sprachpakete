import urllib.request
import json
import ssl

ctx = ssl._create_unverified_context()
queries = [
    "spongebob hoerspiel",
    "spongebob pizza heimservice",
    "spongebob thaddaeus",
    "spongebob aushilfe gesucht",
    "spongebob heimat suess heimat",
    "spongebob folge"
]

for q in queries:
    url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            d = json.loads(resp.read().decode())
            print(f"=== {q} (Total: {d.get('total', 0)}) ===")
            for t in d.get('data', [])[:5]:
                print(f"  Title: {t.get('title')}")
                print(f"  Album: {t.get('album', {}).get('title')}")
                print(f"  Preview: {t.get('preview')}")
                print("-" * 30)
    except Exception as e:
        print(f"Err {q}: {e}")
