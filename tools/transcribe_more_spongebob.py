import speech_recognition as sr
import soundfile as sf
import os
import glob
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

r = sr.Recognizer()
samples_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples_more"
wav_temp = r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples_more\temp.wav"

files = sorted(glob.glob(os.path.join(samples_dir, "*.mp3")))
print(f"Transcribing {len(files)} new SpongeBob clips...", flush=True)

results = {}
for f in files:
    base = os.path.basename(f)
    try:
        data, samplerate = sf.read(f)
        sf.write(wav_temp, data, samplerate)
        with sr.AudioFile(wav_temp) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language="de-DE")
            print(f"[{base[:26]}]: {text}", flush=True)
            results[base] = text
    except Exception as e:
        results[base] = f"Error: {e}"

if os.path.exists(wav_temp):
    os.remove(wav_temp)

with open(os.path.join(samples_dir, "results.json"), "w", encoding="utf-8") as out_f:
    json.dump(results, out_f, indent=2, ensure_ascii=False)

print("Done transcribing more SpongeBob!", flush=True)
