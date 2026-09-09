import speech_recognition as sr
import soundfile as sf
import os
import glob
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

r = sr.Recognizer()
samples_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_samples"
wav_temp = r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_samples\temp.wav"

files = sorted(glob.glob(os.path.join(samples_dir, "0*.mp3")))
print(f"Transcribing {len(files)} Thaddäus Folge 19 clips...", flush=True)

for f in files:
    base = os.path.basename(f)
    try:
        data, samplerate = sf.read(f)
        sf.write(wav_temp, data, samplerate)
        with sr.AudioFile(wav_temp) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language="de-DE")
            print(f"[{base[:24]}]: {text}", flush=True)
    except Exception as e:
        print(f"[{base[:24]}]: Error ({e})", flush=True)

if os.path.exists(wav_temp):
    os.remove(wav_temp)
print("Done Thaddäus Folge 19!", flush=True)
