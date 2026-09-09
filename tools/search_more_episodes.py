import urllib.request
import json
import ssl
import urllib.parse

ctx = ssl._create_unverified_context()
terms = [
    'spongebob gegenteiltag',
    'spongebob fahrpruefung',
    'spongebob karatefieber',
    'spongebob das original-hoerspiel',
    'thaddaeus zeltlager',
    'spongebob ziesmer'
]

for t in terms:
    u = f'https://api.deezer.com/search?q={urllib.parse.quote(t)}'
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            d = json.loads(r.read().decode())
            print(f"=== {t} ({d.get('total',0)}) ===")
            for item in d.get('data', [])[:3]:
                print(' ', item.get('title'), '|', item.get('album',{}).get('title'), '|', item.get('preview'))
    except Exception as e:
        print(f"Error {t}: {e}")
