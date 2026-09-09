import soundfile as sf
import speech_recognition as sr
import os

r = sr.Recognizer()
audio_file = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples\00_Folge 21 Rubble der Fundhund_Kapitel 02 Rubble der Fundhund .mp3"
data, sr_rate = sf.read(audio_file)
total_duration = len(data) / sr_rate
print(f"Total duration: {total_duration:.2f}s, Sample rate: {sr_rate}")

# Let's slice in 2.5s steps with 0.5s step size (windowing) or detect sentences
# 30 seconds total: let's test 2-second chunks from 10s to 28s
wav_slice = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples\slice.wav"

for start_sec in range(8, 28, 2):
    end_sec = min(start_sec + 3.5, total_duration)
    start_sample = int(start_sec * sr_rate)
    end_sample = int(end_sec * sr_rate)
    chunk = data[start_sample:end_sample]
    sf.write(wav_slice, chunk, sr_rate)
    try:
        with sr.AudioFile(wav_slice) as src:
            audio = r.record(src)
            text = r.recognize_google(audio, language="de-DE")
            print(f"{start_sec:02d}s - {end_sec:02.1f}s: {text}")
    except Exception as e:
        # print(f"{start_sec:02d}s - {end_sec:02.1f}s: (silence/unclear)")
        pass

if os.path.exists(wav_slice):
    os.remove(wav_slice)
