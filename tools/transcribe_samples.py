import speech_recognition as sr
import soundfile as sf
import os
import glob
import json
import sys

r = sr.Recognizer()
samples_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples"
wav_temp = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples\temp.wav"

files = sorted(glob.glob(os.path.join(samples_dir, "*.mp3")))
print(f"Found {len(files)} files to transcribe.", flush=True)

results = {}

for f in files:
    base = os.path.basename(f)
    try:
        data, samplerate = sf.read(f)
        sf.write(wav_temp, data, samplerate)
        with sr.AudioFile(wav_temp) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language="de-DE")
            print(f"[{base[:24]}]: {text}", flush=True)
            results[base] = text
    except Exception as e:
        print(f"[{base[:24]}]: Error ({e})", flush=True)
        results[base] = f"Error: {e}"

with open(os.path.join(samples_dir, "results.json"), "w", encoding="utf-8") as out_f:
    json.dump(results, out_f, indent=2, ensure_ascii=False)

if os.path.exists(wav_temp):
    os.remove(wav_temp)
print("Done!", flush=True)
