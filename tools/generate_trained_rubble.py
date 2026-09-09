import os
import sys
import time
import subprocess
from pathlib import Path
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ffmpeg_shared_bin = r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build-shared\bin"
if os.path.exists(ffmpeg_shared_bin) and ffmpeg_shared_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_shared_bin + os.pathsep + os.environ.get("PATH", "")

API_KEY = "sk-fish-ngV4tP1Ft-2VAwa6xeG3grjEvoA0bGn6PULhtY1S2rM"
API_URL = "https://api.fish.audio/v1/tts"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "model": "s2.1-pro-free"
}

OUT_DIR = Path(r"c:\Users\PC\Desktop\Waze German Voice\packs\Samples_Neu")
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR = Path(r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_cuts\raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = "0914c177af5a4b59aadb3e670acd56d1"

samples = [
    {
        "suffix": "start",
        "text": "Wau wau! Rubble packt an! Schnall dich gut an, schalt den Bagger ein und auf die Pfoten, fertig, los!"
    },
    {
        "suffix": "blitzer",
        "text": "Wau! Achtung, Blitzer voraus! Nimm schnell die Pfote vom Gas, sonst wird das ein teures Hundeleckerli!"
    }
]

def convert_to_car_mp3(in_file, out_file):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_file),
        "-af", "volume=5.5dB,alimiter=limit=0.95",
        "-ar", "44100",
        "-ac", "1",
        "-b:a", "36k",
        "-c:a", "libmp3lame",
        str(out_file)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print("Synthesizing Rubble German trained samples...")
for s in samples:
    suffix = s["suffix"]
    text = s["text"]
    raw_file = RAW_DIR / f"rubble_trained_{suffix}.mp3"
    out_file = OUT_DIR / f"rubble_trained_{suffix}.mp3"
    
    payload = {
        "text": text,
        "reference_id": MODEL_ID,
        "format": "mp3",
        "mp3_bitrate": 64
    }
    
    success = False
    for attempt in range(3):
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=25)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(raw_file, "wb") as f:
                    f.write(r.content)
                convert_to_car_mp3(raw_file, out_file)
                print(f"Generated {out_file.name} ({out_file.stat().st_size} bytes)")
                success = True
                break
            else:
                print(f"Attempt {attempt+1} HTTP {r.status_code}: {r.text[:60]}")
        except Exception as e:
            print(f"Attempt {attempt+1} error: {e}")
        time.sleep(1.5)
    
    if not success:
        print(f"Failed to generate {suffix}")

print("Done generating Rubble samples!")
