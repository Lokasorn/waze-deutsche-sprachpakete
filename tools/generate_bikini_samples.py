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
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR = OUT_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    # 1. SpongeBob
    {
        "key": "spongebob_mod1",
        "name": "SpongeBob Schwammkopf (Santiago Ziesmer)",
        "model_id": "5ea97971497248e085ead9fad68f4011",
        "category": "spongebob",
        "start": "Hahahahaha! Ich bin bereit, ich bin bereit, ich bin bereit! Schnall dich an, Kumpel! Wir machen heute die Straßen von Bikini Bottom unsicher! Abfahrt!",
        "blitzer": "Wooohoo! Langsamer, fahr langsamer! Da vorne steht ein Blitzer! Wenn Mrs. Puff das sieht, krieg ich meinen Führerschein nie!"
    },
    # 2. Thaddäus (Kinderfreundlich) - Model ca2fc5c4 (Ruhig / Sarkastisch)
    {
        "key": "thaddaeus_kind_mod1",
        "name": "Thaddäus Kinderfreundlich (Ruhig & Sarkastisch)",
        "model_id": "ca2fc5c4a4c94a0786b79dab81f8f712",
        "category": "thaddaeus_kind",
        "start": "Seufz... Muss das denn wirklich sein? Na schön. Zünd den Motor an und fahr einfach ganz ruhig los, damit ich in Ruhe meine Klarinette üben kann.",
        "blitzer": "Achtung. Da vorne steht ein Blitzer. Brems gefälligst ab, ich habe keine Lust, mein hart verdientes Geld an die Stadt zu verschwenden."
    },
    # 2b. Thaddäus (Kinderfreundlich) - Model c4a08c39 (Mit ruhigem Text)
    {
        "key": "thaddaeus_kind_mod2",
        "name": "Thaddäus Kinderfreundlich (Genervter Nachbar)",
        "model_id": "c4a08c396711407db2d995804772ec09",
        "category": "thaddaeus_kind",
        "start": "Seufz... Guten Tag. Bitte fahr einfach ordentlich und ohne alberne Witze. Ich möchte einfach nur pünktlich ankommen.",
        "blitzer": "Pass mal auf da vorne. Da steht ein Blitzer. Schön das Tempolimit einhalten, sonst gibt's ein Bußgeld."
    },
    # 3. Thaddäus (Rage Modus) - Model c4a08c39 (Wütend / Laut)
    {
        "key": "thaddaeus_rage_mod1",
        "name": "Thaddäus Rage Modus 1 (Voller Wutanfall)",
        "model_id": "c4a08c396711407db2d995804772ec09",
        "category": "thaddaeus_rage",
        "start": "SPONGEBOB! Hör auf zu lachen und fahr endlich los! Schnall dich an, du Hohlkopf! Ich will einfach nur nach Hause in mein Bett! GIB JETZT ENDLICH GAS!",
        "blitzer": "BIST DU DENN VÖLLIG WAHNSINNIG?! TRITT AUF DIE BREMSE! DA STEHT EIN BLITZER! Du bringst uns noch alle ins Grab, du Idiot!"
    },
    # 3b. Thaddäus (Rage Modus) - Model ca2fc5c4 (Wütend)
    {
        "key": "thaddaeus_rage_mod2",
        "name": "Thaddäus Rage Modus 2 (Hysterisch Ausrastend)",
        "model_id": "ca2fc5c4a4c94a0786b79dab81f8f712",
        "category": "thaddaeus_rage",
        "start": "ICH HALTE DAS NICHT MEHR AUS! Fahr sofort los und halt die Klappe! Wenn du noch einmal hupst, raste ich komplett aus!",
        "blitzer": "BREMSEN! DA IST EIN BLITZER, DU VOLLPFOSTEN! Willst du deinen Führerschein verlieren oder was?! TRITT AUF DIE BREMSE!"
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

def generate(item):
    for suffix, text in [("start", item["start"]), ("blitzer", item["blitzer"])]:
        raw_file = RAW_DIR / f"{item['key']}_{suffix}.mp3"
        out_file = OUT_DIR / f"{item['key']}_{suffix}.mp3"
        
        payload = {
            "text": text,
            "reference_id": item["model_id"],
            "format": "mp3",
            "mp3_bitrate": 64
        }
        for attempt in range(3):
            try:
                r = requests.post(API_URL, headers=headers, json=payload, timeout=25)
                if r.status_code == 200 and len(r.content) > 1000:
                    with open(raw_file, "wb") as f:
                        f.write(r.content)
                    convert_to_car_mp3(raw_file, out_file)
                    print(f"  OK: {out_file.name} ({out_file.stat().st_size} bytes)")
                    break
                else:
                    print(f"  Attempt {attempt+1} HTTP {r.status_code}")
            except Exception as e:
                print(f"  Attempt {attempt+1} err: {e}")
            time.sleep(1.2)

print("=== Generating Bikini Bottom Samples ===")
for cand in CANDIDATES:
    print(f"Generating for: {cand['name']}...")
    generate(cand)

print("Done generating Bikini Bottom samples!")
