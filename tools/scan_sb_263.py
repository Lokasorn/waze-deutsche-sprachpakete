import soundfile as sf
import speech_recognition as sr
import glob
import os

r = sr.Recognizer()
files = sorted(glob.glob(r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples_more\*Folge_263*.mp3"))
temp_wav = r"c:\Users\PC\Desktop\Waze German Voice\tools\temp_sb_scan.wav"

for f in files[:4]:
    base = os.path.basename(f)
    data, sr_rate = sf.read(f)
    dur = len(data) / sr_rate
    print(f"\n--- Scanning {base} ({dur:.1f}s) ---")
    t = 0.0
    while t + 3.0 <= dur:
        chunk = data[int(t * sr_rate):int((t + 3.0) * sr_rate)]
        sf.write(temp_wav, chunk, sr_rate)
        try:
            with sr.AudioFile(temp_wav) as src_audio:
                audio = r.record(src_audio)
                txt = r.recognize_google(audio, language="de-DE")
                print(f"  {t:04.1f}s - {t+3.0:04.1f}s: {txt}")
        except:
            pass
        t += 2.0

if os.path.exists(temp_wav):
    os.remove(temp_wav)
