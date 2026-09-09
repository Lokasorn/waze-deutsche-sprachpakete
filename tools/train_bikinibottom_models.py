import requests
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "sk-fish-ngV4tP1Ft-2VAwa6xeG3grjEvoA0bGn6PULhtY1S2rM"
headers = {"Authorization": f"Bearer {API_KEY}"}

models_to_train = [
    {
        "key": "spongebob",
        "title": "SpongeBob Schwammkopf (Deutsch - Santiago Ziesmer)",
        "file": r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_clean_voice.wav",
        "voice_name": "spongebob_de.wav"
    },
    {
        "key": "thaddaeus_kind",
        "title": "Thaddäus Tentakel (Kinderfreundlich - Eberhard Prüter)",
        "file": r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_kind_voice.wav",
        "voice_name": "thaddaeus_kind_de.wav"
    },
    {
        "key": "thaddaeus_rage",
        "title": "Thaddäus Tentakel (Rage Modus - Eberhard Prüter)",
        "file": r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_rage_voice.wav",
        "voice_name": "thaddaeus_rage_de.wav"
    }
]

results = {}

for m in models_to_train:
    print(f"\n--- Training model: {m['title']} ---")
    cut_path = Path(m['file'])
    if not cut_path.exists():
        print(f"Error: File not found {cut_path}")
        continue
    with open(cut_path, "rb") as f:
        audio_data = f.read()

    files = [("voices", (m['voice_name'], audio_data, "audio/wav"))]
    data = {
        "type": "tts",
        "title": m['title'],
        "train_mode": "fast"
    }

    resp = requests.post("https://api.fish.audio/model", headers=headers, data=data, files=files, timeout=60)
    print(f"Response status: {resp.status_code}")
    if resp.status_code in [200, 201]:
        obj = resp.json()
        model_id = obj.get("_id")
        print(f"SUCCESS! Created Model ID: {model_id}")
        results[m['key']] = {
            "title": m['title'],
            "model_id": model_id,
            "raw": obj
        }
    else:
        print(f"Failed: {resp.text}")

out_path = r"c:\Users\PC\Desktop\Waze German Voice\tools\new_bikinibottom_models.json"
with open(out_path, "w", encoding="utf-8") as f_out:
    json.dump(results, f_out, indent=2, ensure_ascii=False)

print(f"\nAll models saved to {out_path}")
