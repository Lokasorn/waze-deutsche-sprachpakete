import soundfile as sf
import numpy as np

src = r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_samples\00_Folge 19 Das Original-Hörspiel zur TV-Serie_Thaddäus streikt.mp3"
dst = r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_kind_voice.wav"

data, sr = sf.read(src)
# Let's extract 04.0s to 18.0s
start_sec = 4.2
end_sec = 18.0
cut = data[int(start_sec * sr):int(end_sec * sr)]

sf.write(dst, cut, sr)
dur = len(cut) / sr
print(f"Extracted Thaddaeus Kinderfreundlich voice: {dur:.2f}s to {dst}")
