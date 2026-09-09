import soundfile as sf
import speech_recognition as sr
import os

r = sr.Recognizer()
wav_slice = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples\slice2.wav"

def check_file(audio_path):
    print(f"\n--- Checking {os.path.basename(audio_path)} ---", flush=True)
    data, sr_rate = sf.read(audio_path)
    total_dur = len(data) / sr_rate
    for s in range(0, int(total_dur) - 3, 2):
        chunk = data[int(s*sr_rate):int((s+3.5)*sr_rate)]
        sf.write(wav_slice, chunk, sr_rate)
        try:
            with sr.AudioFile(wav_slice) as src:
                t = r.recognize_google(r.record(src), language="de-DE")
                print(f"{s:02d}s - {s+3.5:04.1f}s: {t}", flush=True)
        except Exception:
            pass

check_file(r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples\01_Folge 21 Rubble der Fundhund_Kapitel 03 Rubble der Fundhund .mp3")
check_file(r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples\02_Folge 21 Rubble der Fundhund_Kapitel 05 Rubble der Fundhund .mp3")

if os.path.exists(wav_slice):
    os.remove(wav_slice)
