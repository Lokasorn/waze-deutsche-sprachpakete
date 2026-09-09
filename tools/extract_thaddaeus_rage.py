import soundfile as sf
import numpy as np

src = r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_samples\03_Folge 19 Das Original-Hörspiel zur TV-Serie_Thaddäus streikt.mp3"
dst = r"c:\Users\PC\Desktop\Waze German Voice\tools\thaddaeus_rage_voice.wav"

data, sr = sf.read(src)

# Segment 1: 0.0s to 4.2s ("das Großkapital in seine Grundfesten erschüttern...")
seg1 = data[0:int(4.2 * sr)]

# Segment 2: 17.2s to 24.5s ("mit eurer Unterstützung wird die geballte Faust des Volkes...")
seg2 = data[int(17.2 * sr):int(24.5 * sr)]

# Small silence between segments (0.3s)
silence = np.zeros(int(0.3 * sr), dtype=seg1.dtype) if seg1.ndim == 1 else np.zeros((int(0.3 * sr), seg1.shape[1]), dtype=seg1.dtype)

combined = np.concatenate([seg1, silence, seg2])
sf.write(dst, combined, sr)

dur = len(combined) / sr
print(f"Created Thaddaeus Rage Voice: {dur:.2f}s -> {dst}")
