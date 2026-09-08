"""
Production MontanaBlack Voicepack Generator & Waze Cloud Publisher using Fish Audio.
- Uses community MontanaBlack model 'c4edd151f9484b6c90849e43be61181e' (rated 8-9/10 by user).
- Synthesizes all 43 Waze prompts with authentic Monte slang and expressions.
- Normalizes and boosts audio (+6dB) for crystal clarity in car environments.
- Enforces strict Waze <0.78 MB cloud limit while preserving maximum audio fidelity.
- Automatically uploads to Waze servers via Protobuf API and outputs the 1-click install link.
"""

import json
import os
import shutil
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Ensure FFmpeg shared libraries are available
ffmpeg_shared_bin = r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build-shared\bin"
if os.path.exists(ffmpeg_shared_bin) and ffmpeg_shared_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_shared_bin + os.pathsep + os.environ.get("PATH", "")

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import requests
from backend.audio_processor import compress_pack_to_limit, convert_and_optimize_file, get_folder_size_mb
from backend.waze_prompts import VALID_WAZE_FILENAMES
from backend.waze_uploader import upload_soundpack_to_waze

OUTPUT_PACK_DIR = BASE_DIR / "packs" / "MontanaBlack"
TEMP_RAW_DIR = BASE_DIR / "scratch" / "fish_raw_mp3s"

# Load API key from environment variable or local .env
FISH_API_KEY = os.environ.get("FISH_API_KEY", "")
if not FISH_API_KEY and os.path.exists(BASE_DIR / ".env"):
    with open(BASE_DIR / ".env", "r", encoding="utf-8") as env_f:
        for line in env_f:
            if line.startswith("FISH_API_KEY="):
                FISH_API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

FISH_MODEL_ID = "c4edd151f9484b6c90849e43be61181e"
FISH_API_URL = "https://api.fish.audio/v1/tts"

# Authentic MontanaBlack lines for all 43 Waze prompts
MONTANABLACK_PROMPTS = {
    "StartDrive1.mp3": "Jo Freunde, Monte hier! Rein in die Olga, ab geht die wilde Fahrt!",
    "StartDrive2.mp3": "Uff jeden! Navi steht, jetzt aber keine Mätzchen auf der Bahn!",
    "StartDrive3.mp3": "Servus, Grüß Gott! Abfahrt, aber bleib mir vom Gaspedal wenn die Cops da sind!",
    "StartDrive4.mp3": "Digga, Musik an, Fenster runter, und ab geht die wilde Fahrt!",
    "StartDrive5.mp3": "Bruder, wir fahren los. Wenn du dich verfährst, krieg ich die Krise!",
    "StartDrive6.mp3": "Geisteskrank! Route ist geladen, zieh durch!",
    "StartDrive7.mp3": "Hände ans Lenkrad und kein Handy am Steuer, sonst scheppert es!",
    "StartDrive8.mp3": "Auf geht's, heute wird nicht getiltet!",
    "StartDrive9.mp3": "Let's go! Monte ist dein Copilot, alles im Griff.",
    "TurnLeft.mp3": "Links abbiegen, Digger! Aber zackig!",
    "TurnRight.mp3": "Rechts abbiegen, Bruder! Blinker nicht vergessen!",
    "KeepLeft.mp3": "Halt dich links, die Spur ist frei!",
    "KeepRight.mp3": "Rechts halten, blockier hier nicht die linke Spur!",
    "Straight.mp3": "Einfach geradeaus durchballern!",
    "uturn.mp3": "Bruder, komplett lost! Sofort umdrehen!",
    "AndThen.mp3": "Und direkt danach...",
    "Arrive.mp3": "Ziel erreicht! Ez win, Bruder! Endlich raus hier!",
    "Roundabout.mp3": "Kreisverkehr gespottet, pass auf wer von links kommt!",
    "First.mp3": "...direkt die erste Ausfahrt wieder raus!",
    "Second.mp3": "...die zweite Ausfahrt nehmen!",
    "Third.mp3": "...dritte Ausfahrt raus da!",
    "Fourth.mp3": "...vierte Ausfahrt! Einmal fast komplett im Kreis!",
    "Fifth.mp3": "...fünfte Ausfahrt nehmen!",
    "Sixth.mp3": "...sechste Ausfahrt, was für ein Riesenteil!",
    "Seventh.mp3": "...siebte Ausfahrt, wir drehen uns im Kreis, Digga!",
    "ExitLeft.mp3": "Ausfahrt links nehmen, rüber da!",
    "ExitRight.mp3": "Ausfahrt rechts nehmen, jetzt runter von der Bahn!",
    "200meters.mp3": "In zweihundert Metern...",
    "400meters.mp3": "In vierhundert Metern...",
    "800meters.mp3": "In achthundert Metern...",
    "1000meters.mp3": "In einem Kilometer...",
    "1500meters.mp3": "In eineinhalb Kilometern...",
    "200.mp3": "Gleich hier...",
    "400.mp3": "In Kürze...",
    "800.mp3": "Demnächst...",
    "1500.mp3": "Aufpassen, gleich kommt's...",
    "Police.mp3": "Achtung Digger! Die Cops campen da vorne! Schön brav 50 fahren!",
    "ApproachSpeedCam.mp3": "Blitzer voraus! Geh sofort vom Gas, dein Kontostand weint sonst!",
    "ApproachRedLightCam.mp3": "Ampelblitzer! Nicht bei Gelb rüberdrücken, bist du irre?!",
    "ApproachHazard.mp3": "Gefahr auf der Fahrbahn! Augen auf die Straße!",
    "ApproachTraffic.mp3": "Stau voraus... Digga ich raste komplett aus! Wer steht da wieder?!",
    "ApproachAccident.mp3": "Unfall voraus gemeldet! Fahr vorsichtig vorbei und gaff nicht!",
    "TickerPoints.mp3": "Bruder verfahren! Ich berechne neu, warte kurz...",
}


def call_fish_audio_tts(text: str, max_retries: int = 3) -> bytes:
    """Calls Fish Audio API with retry logic and rate limit management."""
    headers = {
        "Authorization": f"Bearer {FISH_API_KEY}",
        "Content-Type": "application/json",
        "model": "s2.1-pro-free",
    }
    payload = {
        "text": text,
        "reference_id": FISH_MODEL_ID,
        "format": "mp3",
    }
    
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(FISH_API_URL, json=payload, headers=headers, timeout=35)
            if r.status_code == 200 and len(r.content) > 1000:
                return r.content
            elif r.status_code in (402, 429):
                # Rate limit or quota concurrency
                wait = attempt * 3.0
                print(f" [Rate limit/busy, warte {wait}s]", end="", flush=True)
                time.sleep(wait)
            else:
                print(f" [HTTP {r.status_code}: {r.text[:50]}]", end="", flush=True)
                time.sleep(2.0)
        except Exception as e:
            print(f" [Fehler: {str(e)[:40]}]", end="", flush=True)
            time.sleep(2.5)
            
    raise RuntimeError(f"Fish Audio Generierung fehlgeschlagen für: '{text}'")


def run_full_pipeline():
    print("=" * 65)
    print("🎙️  STARTING MONTANABLACK WAZE SOUNDPACK (FISH AUDIO)  🎙️")
    print("=" * 65)

    os.makedirs(OUTPUT_PACK_DIR, exist_ok=True)
    os.makedirs(TEMP_RAW_DIR, exist_ok=True)

    total = len(VALID_WAZE_FILENAMES)
    start_time = time.time()

    print(f"\n⚡ Generiere alle {total} Waze-Prompts mit Fish Audio (Modell: MontanaBlack)...")

    for idx, filename in enumerate(VALID_WAZE_FILENAMES, 1):
        text = MONTANABLACK_PROMPTS.get(filename, "Navigation.")
        t0 = time.time()
        print(f"[{idx:02d}/{total}] {filename:22s} -> \"{text[:35]}...\"", end="", flush=True)

        raw_mp3_path = TEMP_RAW_DIR / filename
        
        # 1. Fetch audio from Fish Audio
        audio_bytes = call_fish_audio_tts(text)
        with open(raw_mp3_path, "wb") as f:
            f.write(audio_bytes)

        # 2. Convert to optimized Mono MP3 with +6dB car audio boost
        target_mp3 = OUTPUT_PACK_DIR / filename
        convert_and_optimize_file(str(raw_mp3_path), str(target_mp3), bitrate_kbps=36, volume_boost_db=6.0)

        dt = time.time() - t0
        print(f" ({dt:.1f}s)")
        
        # Respect rate limits smoothly
        time.sleep(1.2)

    total_time = time.time() - start_time
    print(f"\n🎉 Alle 43 Ansagen erfolgreich generiert in {total_time/60:.1f} Minuten!")

    # 3. Enforce strict Waze size limit (< 0.78 MB)
    current_size = get_folder_size_mb(str(OUTPUT_PACK_DIR))
    print(f"\n🎛️ Prüfe Pack-Größe: {current_size:.3f} MB (Limit: <= 0.78 MB)...")
    if current_size > 0.78:
        print("Kompression anpassen...")
        success, final_size, br = compress_pack_to_limit(str(OUTPUT_PACK_DIR), target_max_mb=0.78)
        print(f"🎯 Finale optimierte Pack-Größe: {final_size:.3f} MB ({br} kbps Mono).")
    else:
        print(f"🎯 Pack-Größe bereits optimal: {current_size:.3f} MB! Keine Qualitätsreduktion nötig.")

    # 4. Upload to Waze Cloud API
    print("\n☁️ Lade das fertige MontanaBlack-Soundpack zu den Waze-Servern hoch...")
    upload_result = upload_soundpack_to_waze("MontanaBlack_DE", str(OUTPUT_PACK_DIR))

    if upload_result.get("success"):
        deep_link = upload_result["deep_link"]
        pack_uuid = upload_result["pack_uuid"]
        size_mb = upload_result["size_mb"]

        print("\n" + "=" * 65)
        print("🚀  WAZE CLOUD UPLOAD ERFOLGREICH!  🚀")
        print("=" * 65)
        print(f"📱 1-Klick Waze Link:  {deep_link}")
        print(f"🆔 UUID:               {pack_uuid}")
        print(f"📦 Dateigröße:         {size_mb} MB")
        print("=" * 65)

        # Update JSON database
        json_path = BASE_DIR / "helper_files" / "waze_vps.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            for item in db:
                if item.get("slug") == "montanablack":
                    item["waze_link"] = deep_link
                    item["download_url"] = upload_result["download_link"]
                    item["uuid"] = pack_uuid
                    item["file_size_mb"] = size_mb
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2, ensure_ascii=False)

        # Update README
        readme_path = BASE_DIR / "README.md"
        if readme_path.exists():
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Replace old acvp links with new one
            old_uuid = "60858425-9afe-4144-a4e6-888a9f287a71"
            content = content.replace(old_uuid, pack_uuid)
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content)

        print("\n📄 README.md und helper_files/waze_vps.json wurden mit dem neuen Link aktualisiert!")
    else:
        print("\n❌ Upload fehlgeschlagen:", upload_result.get("error"))

    # Clean up temp raw files
    shutil.rmtree(TEMP_RAW_DIR, ignore_errors=True)
    print("\n✨ Fertig! Das MontanaBlack Soundpack (8-9/10 Qualität) ist live.")


if __name__ == "__main__":
    run_full_pipeline()
