import soundfile as sf
import speech_recognition as sr
import os

r = sr.Recognizer()
f00 = r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_samples\00_Folge 19 Das Original-Hörspiel zur TV-Serie_Thaddäus streikt.mp3"
f03 = r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_samples\03_Folge 19 Das Original-Hörspiel zur TV-Serie_Thaddäus streikt.mp3"
temp_wav = r"c:\Users\PC\Desktop\Waze German Voice\tools\temp_scan.wav"

def scan_file(filepath, name, step=2.0, win=3.5):
    data, sr_rate = sf.read(filepath)
    dur = len(data) / sr_rate
    print(f"\n=== Scanning {name} (Total: {dur:.1f}s) ===")
    t = 0.0
    while t + win <= dur:
        start_samp = int(t * sr_rate)
        end_samp = int((t + win) * sr_rate)
        chunk = data[start_samp:end_samp]
        sf.write(temp_wav, chunk, sr_rate)
        try:
            with sr.AudioFile(temp_wav) as src:
                audio = r.record(src)
                txt = r.recognize_google(audio, language="de-DE")
                print(f"  {t:04.1f}s - {t+win:04.1f}s: {txt}")
        except:
            pass
        t += step

if __name__ == "__main__":
    scan_file(f03, "03_Folge 19 (Megaphone / Rage)")
    if os.path.exists(temp_wav):
        os.remove(temp_wav)
