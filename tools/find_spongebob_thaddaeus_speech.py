import soundfile as sf
import speech_recognition as sr
import os
import glob

r = sr.Recognizer()
wav_slice = r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples\slice.wav"

def scan_file(filepath, label):
    print(f"\n=== Scanning {label} ({os.path.basename(filepath)[:35]}) ===", flush=True)
    try:
        data, sr_rate = sf.read(filepath)
        dur = len(data) / sr_rate
        for s in range(0, int(dur) - 2, 2):
            chunk = data[int(s * sr_rate):int((s + 3.0) * sr_rate)]
            sf.write(wav_slice, chunk, sr_rate)
            try:
                with sr.AudioFile(wav_slice) as src:
                    t = r.recognize_google(r.record(src), language="de-DE")
                    print(f"  {s:02d}s - {s+3.0:04.1f}s: {t}", flush=True)
            except Exception:
                pass
    except Exception as e:
        print(f"Error {filepath}: {e}", flush=True)

th_files = glob.glob(r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_samples\0*.mp3")
if th_files:
    scan_file(th_files[0], "Thaddaeus Streikt 00")

sb_files = glob.glob(r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples\05*.mp3")
if sb_files:
    scan_file(sb_files[0], "Pizza 05")

sb6_files = glob.glob(r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples\06*.mp3")
if sb6_files:
    scan_file(sb6_files[0], "Pizza 06")

if os.path.exists(wav_slice):
    os.remove(wav_slice)
