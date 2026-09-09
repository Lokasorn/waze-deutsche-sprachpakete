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

OUT_DIR = Path(r"c:\Users\PC\Desktop\Waze German Voice\packs\Samples_BikiniBottom")
RAW_DIR = OUT_DIR / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

NEW_MODELS = [
    {
        "key": "spongebob_trained",
        "name": "Neu trainiert: Deutsche Originalstimme (Santiago Ziesmer)",
        "model_id": "01f717b1864a44719d88934f841d52ff",
        "category": "spongebob",
        "start": "Hahahahaha! Ich bin bereit, ich bin bereit, ich bin bereit! Schnall dich an, Kumpel! Wir machen heute die Straßen von Bikini Bottom unsicher! Abfahrt!",
        "blitzer": "Wooohoo! Langsamer, fahr langsamer! Da vorne steht ein Blitzer! Wenn Mrs. Puff das sieht, krieg ich meinen Führerschein nie!"
    },
    {
        "key": "thaddaeus_kind_trained",
        "name": "Neu trainiert: Deutsche Originalstimme (Eberhard Prüter)",
        "model_id": "8d1e3f20f3af41649511dc2434919c98",
        "category": "thaddaeus_kind",
        "start": "Seufz... Muss das denn wirklich sein? Na schön. Zünd den Motor an und fahr einfach ganz ruhig los, damit ich in Ruhe meine Klarinette üben kann.",
        "blitzer": "Achtung. Da vorne steht ein Blitzer. Brems gefälligst ab, ich habe keine Lust, mein hart verdientes Geld an die Stadt zu verschwenden."
    },
    {
        "key": "thaddaeus_rage_trained",
        "name": "Neu trainiert: Deutsche Originalstimme (Eberhard Prüter - Rage)",
        "model_id": "0f256abef80f45a38cce0c71d1b02f3a",
        "category": "thaddaeus_rage",
        "start": "SPONGEBOB! Hör auf zu lachen und fahr endlich los! Schnall dich an, du Hohlkopf! Ich will einfach nur nach Hause in mein Bett! GIB JETZT ENDLICH GAS!",
        "blitzer": "BIST DU DENN VÖLLIG WAHNSINNIG?! TRITT AUF DIE BREMSE! DA STEHT EIN BLITZER! Du bringst uns noch alle ins Grab, du Idiot!"
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

print("Starting TTS generation for newly trained models...")

for item in NEW_MODELS:
    print(f"\nGenerating samples for: {item['name']} ({item['model_id']})")
    for suffix, text in [("start", item["start"]), ("blitzer", item["blitzer"])]:
        raw_file = RAW_DIR / f"{item['key']}_{suffix}.mp3"
        out_file = OUT_DIR / f"{item['key']}_{suffix}.mp3"
        
        payload = {
            "text": text,
            "reference_id": item["model_id"],
            "format": "mp3",
            "mp3_bitrate": 64
        }
        
        success = False
        for attempt in range(3):
            try:
                res = requests.post(API_URL, headers=headers, json=payload, timeout=30)
                if res.status_code == 200:
                    with open(raw_file, "wb") as f:
                        f.write(res.content)
                    convert_to_car_mp3(raw_file, out_file)
                    print(f"  [OK] {item['key']}_{suffix}.mp3 ({len(res.content)}b raw -> {out_file.stat().st_size}b car)")
                    success = True
                    break
                else:
                    print(f"  [Attempt {attempt+1}] Error: {res.status_code} - {res.text[:100]}")
                    time.sleep(2)
            except Exception as e:
                print(f"  [Attempt {attempt+1}] Exception: {e}")
                time.sleep(2)
        if not success:
            print(f"  [FAIL] Could not generate {item['key']}_{suffix}")

print("\nFinished generating all trained test samples!")
