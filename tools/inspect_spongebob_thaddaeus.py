import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "7e8910080ae94576a91f52b0f4fa6e89"
headers = {"Authorization": f"Bearer {API_KEY}"}

model_ids = [
    ("5ea97971497248e085ead9fad68f4011", "Spongebob (Santiago Ziesmer)"),
    ("c4a08c396711407db2d995804772ec09", "Thaddäus 1"),
    ("ca2fc5c4a4c94a0786b79dab81f8f712", "Thaddäus 2")
]

for mid, name in model_ids:
    url = f"https://api.fish.audio/model/{mid}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"=== {name} ({mid}) ===")
            print(f"  Title: {data.get('title')}")
            print(f"  Description: {data.get('description')}")
            print(f"  Languages: {data.get('languages')}")
            print(f"  Tags: {data.get('tags')}")
            print(f"  Author: {data.get('author', {}).get('nickname')}")
    except Exception as e:
        print(f"  Err {mid}: {e}")
