import requests
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "sk-fish-ngV4tP1Ft-2VAwa6xeG3grjEvoA0bGn6PULhtY1S2rM"
headers = {"Authorization": f"Bearer {API_KEY}"}

cut_path = Path(r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_cuts\rubble_german_clean.wav")

with open(cut_path, "rb") as f:
    audio_data = f.read()

files = [("voices", ("rubble_de.wav", audio_data, "audio/wav"))]
data = {
    "type": "tts",
    "title": "Paw Patrol Rubble (Deutsch - Ivo Möller)",
    "train_mode": "fast"
}

print("Uploading Rubble German voice sample to Fish Audio model creation API...")
r = requests.post("https://api.fish.audio/model", headers=headers, data=data, files=files, timeout=40)
print("Status:", r.status_code)
if r.status_code in [200, 201]:
    model_obj = r.json()
    model_id = model_obj.get("_id")
    print("SUCCESS: Rubble German Model created with ID:", model_id)
    with open(r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_cuts\new_rubble_model.json", "w", encoding="utf-8") as f_out:
        json.dump(model_obj, f_out, indent=2, ensure_ascii=False)
else:
    print("Error:", r.text)
