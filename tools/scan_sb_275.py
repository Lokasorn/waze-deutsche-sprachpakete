import soundfile as sf
import speech_recognition as sr
import glob
import os
import sys

r = sr.Recognizer()
files = sorted(glob.glob(r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples_more\*00_Folge_275*.mp3"))
if files:
    src = files[0]
    data, sr_rate = sf.read(src)
    dur = len(data) / sr_rate
    print(f"Scanning {src} ({dur:.1f}s)...", flush=True)
    temp_wav = r"c:\Users\PC\Desktop\Waze German Voice\tools\temp_sb275.wav"
    t = 0.0
    while t + 3.0 <= dur:
        chunk = data[int(t * sr_rate):int((t + 3.0) * sr_rate)]
        sf.write(temp_wav, chunk, sr_rate)
        try:
            with sr.AudioFile(temp_wav) as src_audio:
                audio = r.record(src_audio)
                txt = r.recognize_google(audio, language="de-DE")
                print(f"  {t:04.1f}s - {t+3.0:04.1f}s: {txt}", flush=True)
        except:
            pass
        t += 1.5
    if os.path.exists(temp_wav):
        os.remove(temp_wav)
