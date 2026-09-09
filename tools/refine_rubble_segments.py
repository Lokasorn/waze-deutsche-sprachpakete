import soundfile as sf
import speech_recognition as sr
import os
import numpy as np

r = sr.Recognizer()
wav_tmp = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_cuts\temp_refine.wav"

def test_slice(audio_path, start, end, label):
    data, sr_rate = sf.read(audio_path)
    s_idx = int(start * sr_rate)
    e_idx = int(end * sr_rate)
    chunk = data[s_idx:e_idx]
    sf.write(wav_tmp, chunk, sr_rate)
    with sr.AudioFile(wav_tmp) as src:
        try:
            t = r.recognize_google(r.record(src), language="de-DE")
            print(f"[{label}] {start:.2f}s - {end:.2f}s: '{t}'")
        except Exception as e:
            print(f"[{label}] {start:.2f}s - {end:.2f}s: (Error: {e})")

samples_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples"
f02 = os.path.join(samples_dir, "02_Folge 21 Rubble der Fundhund_Kapitel 05 Rubble der Fundhund .mp3")
f03 = os.path.join(samples_dir, "03_Folge 21 Rubble der Fundhund_Kapitel 04 Rubble der Fundhund .mp3")
f00 = os.path.join(samples_dir, "00_Folge 21 Rubble der Fundhund_Kapitel 02 Rubble der Fundhund .mp3")

print("--- Testing f02: 'Ja und wie! Tolles Auto! Danke, dass du mich mitgenommen hast!' ---")
test_slice(f02, 7.8, 12.3, "f02_rubble_pure")
test_slice(f02, 8.0, 12.0, "f02_rubble_tighter")

print("--- Testing f03: 'Ich buddel total gern!' ---")
test_slice(f03, 13.0, 16.0, "f03_buddel")
test_slice(f03, 13.5, 15.5, "f03_buddel_tight")

print("--- Testing f00: 'Du hast ja eine tolle Ausrüstung...' ---")
test_slice(f00, 16.2, 21.0, "f00_ausruestung")
test_slice(f00, 24.8, 27.5, "f00_verspreche")

if os.path.exists(wav_tmp):
    os.remove(wav_tmp)
