"""
Autonomous MontanaBlack Voice Cloning & Waze Pack Publisher.
Uses F5-TTS to clone MontanaBlack's real voice from reference audio (Rein in die Olga),
synthesizes all 43 Waze navigation prompts with authentic Monte slang,
converts/boosts audio for car acoustics (+7dB), enforces the <0.8MB Waze limit,
and uploads the voicepack directly to Waze servers.
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Setup paths and environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Ensure FFmpeg shared libraries are available for torchcodec and pydub
ffmpeg_shared_bin = r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build-shared\bin"
if os.path.exists(ffmpeg_shared_bin) and ffmpeg_shared_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_shared_bin + os.pathsep + os.environ.get("PATH", "")

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import soundfile as sf
from cached_path import cached_path
from f5_tts.infer.utils_infer import infer_process, load_model, load_vocoder, preprocess_ref_audio_text
from hydra.utils import get_class, instantiate
from omegaconf import OmegaConf

from backend.audio_processor import compress_pack_to_limit, convert_and_optimize_file, get_folder_size_mb
from backend.waze_prompts import VALID_WAZE_FILENAMES
from backend.waze_uploader import upload_soundpack_to_waze

OUTPUT_PACK_DIR = BASE_DIR / "packs" / "MontanaBlack"
TEMP_WAV_DIR = BASE_DIR / "scratch" / "f5_monte_wavs"
REF_AUDIO = str(BASE_DIR / "training_data" / "montanablack" / "rein_in_die_olga.mp3")
REF_TEXT = "Rein in die Olga!"

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


def run_full_pipeline():
    print("=" * 65)
    print("🎙️  STARTING MONTANABLACK AI VOICE CLONING (F5-TTS)  🎙️")
    print("=" * 65)

    os.makedirs(OUTPUT_PACK_DIR, exist_ok=True)
    os.makedirs(TEMP_WAV_DIR, exist_ok=True)

    # 1. Load F5-TTS model and vocoder into memory once
    device = "cpu"
    print("\n📦 Lade F5-TTS Modell & Vocoder in den Arbeitsspeicher...")
    import f5_tts
    f5_root = Path(list(f5_tts.__path__)[0])
    model_cfg = OmegaConf.load(str(f5_root / "configs" / "F5TTS_v1_Base.yaml"))

    model_cls = get_class(f"f5_tts.model.{model_cfg.model.backbone}")
    model_arc = model_cfg.model.arch
    ckpt_file = str(cached_path("hf://SWivid/F5-TTS/F5TTS_v1_Base/model_1250000.safetensors"))
    vocab_file = str(f5_root / "infer" / "examples" / "vocab.txt")

    ema_model = load_model(
        model_cls, model_arc, ckpt_file, mel_spec_type="vocos", vocab_file=vocab_file, device=device
    )
    vocoder = load_vocoder(vocoder_name="vocos", device=device)
    print("✅ Modell erfolgreich geladen!")

    # 2. Preprocess reference audio of MontanaBlack
    print(f"\n🎧 Verarbeite Referenz-Audio: {REF_AUDIO} (Text: '{REF_TEXT}')")
    processed_ref_audio, processed_ref_text = preprocess_ref_audio_text(REF_AUDIO, REF_TEXT)

    # 3. Generate all 43 prompts with voice cloning
    print("\n⚡ Starte KI-Stimmensynthese für alle 43 Waze-Befehle:")
    total = len(VALID_WAZE_FILENAMES)
    start_time = time.time()

    for idx, filename in enumerate(VALID_WAZE_FILENAMES, 1):
        gen_text = MONTANABLACK_PROMPTS.get(filename, "Navigation.")
        t0 = time.time()
        print(f"[{idx:02d}/{total}] Klone {filename:20s} -> \"{gen_text[:40]}...\"", end="", flush=True)

        audio_segment, final_sample_rate, _ = infer_process(
            processed_ref_audio,
            processed_ref_text,
            gen_text,
            ema_model,
            vocoder,
            mel_spec_type="vocos",
            target_rms=0.1,
            cross_fade_duration=0.15,
            nfe_step=12,
            cfg_strength=2.0,
            speed=1.05,
            device=device,
        )

        # Save raw WAV
        raw_wav_path = TEMP_WAV_DIR / f"{filename}.wav"
        sf.write(str(raw_wav_path), audio_segment, final_sample_rate)

        # Convert to Waze Mono MP3 with +7dB car boost
        target_mp3 = OUTPUT_PACK_DIR / filename
        convert_and_optimize_file(str(raw_wav_path), str(target_mp3), bitrate_kbps=32)

        dt = time.time() - t0
        print(f" ({dt:.1f}s)")

    total_time = time.time() - start_time
    print(f"\n🎉 Alle 43 Ansagen mit MontanaBlacks Stimme geklont in {total_time/60:.1f} Minuten!")

    # 4. Enforce Waze size limit (<0.79 MB)
    print("\n🎛️ Optimiere Pack-Größe für Waze Cloud Server...")
    success, final_size, br = compress_pack_to_limit(str(OUTPUT_PACK_DIR), target_max_mb=0.78)
    print(f"🎯 Finale Pack-Größe: {final_size:.3f} MB ({br} kbps Mono).")

    # 5. Upload to Waze Cloud API
    print("\n☁️ Lade das geklonte MontanaBlack-Soundpack zu Waze hoch...")
    upload_result = upload_soundpack_to_waze("MontanaBlack_DE", str(OUTPUT_PACK_DIR))

    if upload_result.get("success"):
        deep_link = upload_result["deep_link"]
        print("\n" + "=" * 65)
        print("🚀  WAZE CLOUD UPLOAD ERFOLGREICH!  🚀")
        print("=" * 65)
        print(f"📱 1-Klick Waze Link:  {deep_link}")
        print(f"🆔 UUID:               {upload_result['pack_uuid']}")
        print(f"📦 Dateigröße:         {upload_result['size_mb']} MB")
        print("=" * 65)

        # Update json database
        import json
        json_path = BASE_DIR / "helper_files" / "waze_vps.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            for item in db:
                if item.get("slug") == "montanablack":
                    item["waze_link"] = deep_link
                    item["download_url"] = upload_result["download_link"]
                    item["uuid"] = upload_result["pack_uuid"]
                    item["file_size_mb"] = upload_result["size_mb"]
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2, ensure_ascii=False)

        # Update README
        readme_path = BASE_DIR / "README.md"
        if readme_path.exists():
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Replace old acvp uuid with new one
            old_uuid = "e80dbf65-cb73-4586-9ca5-5cfb72f6f7a8"
            new_uuid = upload_result["pack_uuid"]
            content = content.replace(old_uuid, new_uuid)
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content)

        print("\n📄 README.md und helper_files/waze_vps.json wurden mit dem neuen Link aktualisiert!")
    else:
        print("\n❌ Upload fehlgeschlagen:", upload_result.get("error"))

    # Clean up temp wavs
    shutil.rmtree(TEMP_WAV_DIR, ignore_errors=True)
    print("\n✨ Fertig! Das MontanaBlack Soundpack mit echter KI-Stimme ist online.")


if __name__ == "__main__":
    run_full_pipeline()
