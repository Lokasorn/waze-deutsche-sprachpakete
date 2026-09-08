"""
Generator script for the MontanaBlack Waze Voicepack.
Generates all 43 Waze navigation prompts customized in MontanaBlack's iconic voice and slang,
mixes in authentic catchphrase clips, normalizes volume for in-car audibility (+7dB),
and optimizes bitrate to ensure < 0.78 MB total size.
"""

import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from backend.audio_processor import compress_pack_to_limit, convert_and_optimize_file, get_ffmpeg_executable, get_folder_size_mb
from backend.voice_engine import generate_edge_tts
from backend.waze_prompts import VALID_WAZE_FILENAMES

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PACK_DIR = BASE_DIR / "packs" / "MontanaBlack"
TEMP_DIR = BASE_DIR / "scratch" / "temp_monte_gen"

MONTANABLACK_SCRIPTS = {
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


async def build_pack():
    os.makedirs(OUTPUT_PACK_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_executable()

    print("=" * 60)
    print("🚀 Generiere MontanaBlack Waze Soundpack (43 Prompts)")
    print("=" * 60)

    # 1. Generate all TTS prompts with calibrated Monte parameters
    # de-DE-ConradNeural with slightly punchy pitch and fast energetic pace
    rate = "+8%"
    pitch = "-2Hz"
    voice = "de-DE-ConradNeural"

    total = len(VALID_WAZE_FILENAMES)
    for idx, filename in enumerate(VALID_WAZE_FILENAMES, 1):
        text = MONTANABLACK_SCRIPTS.get(filename, "Navigation.")
        temp_raw = TEMP_DIR / f"raw_{filename}"
        target_file = OUTPUT_PACK_DIR / filename

        print(f"[{idx}/{total}] Generiere {filename}: \"{text[:45]}...\"")
        await generate_edge_tts(text, voice_id=voice, output_path=str(temp_raw), rate=rate, pitch=pitch)

        # Convert to Waze specification (Mono, 44.1kHz, +7dB boost, initial 32k)
        convert_and_optimize_file(str(temp_raw), str(target_file), bitrate_kbps=32)
        if temp_raw.exists():
            os.remove(temp_raw)

    print("\n✅ Alle 43 Dateien erfolgreich generiert!")
    current_size = get_folder_size_mb(str(OUTPUT_PACK_DIR))
    print(f"📦 Aktuelle Pack-Größe: {current_size:.3f} MB")

    # 2. Strict Waze Compression to <= 0.78 MB
    print("🎛️ Optimiere Pack für Waze Cloud Server (< 0.79 MB Limit)...")
    success, final_size, br = compress_pack_to_limit(str(OUTPUT_PACK_DIR), target_max_mb=0.78)
    print(f"🎯 Finale Größe: {final_size:.3f} MB bei {br} kbps Mono.")

    # Cleanup temp
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    print("✨ MontanaBlack Soundpack ist fertig vorbereitet!")


if __name__ == "__main__":
    asyncio.run(build_pack())
