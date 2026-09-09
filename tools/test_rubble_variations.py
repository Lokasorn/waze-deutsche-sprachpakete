import requests
import json

API_KEY = "sk-fish-ngV4tP1Ft-2VAwa6xeG3grjEvoA0bGn6PULhtY1S2rM"
MODEL_ID = "0914c177af5a4b59aadb3e670acd56d1"

# Let's inspect the model details on Fish Audio first!
res = requests.get(f"https://api.fish.audio/model/{MODEL_ID}", headers={"Authorization": f"Bearer {API_KEY}"})
print("Model info status:", res.status_code)
if res.status_code == 200:
    print("Model info:", json.dumps(res.json(), indent=2)[:400])

# Test short text vs long text with Rubble Welpen prefix
tests = [
    ("short_bare", "In zweihundert Metern..."),
    ("short_prefixed", "Wau! In zweihundert Metern links abbiegen!"),
    ("first_bare", "Nimm die erste Ausfahrt!"),
    ("first_prefixed", "Wau wau! Nimm die erste Ausfahrt!")
]

for label, text in tests:
    payload = {
        "text": text,
        "reference_id": MODEL_ID,
        "format": "mp3",
        "mp3_bitrate": 64
    }
    r = requests.post("https://api.fish.audio/v1/tts", headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }, json=payload)
    print(f"Generated {label}: {r.status_code} ({len(r.content)} bytes)")
    with open(f"tools/test_{label}.mp3", "wb") as f:
        f.write(r.content)
