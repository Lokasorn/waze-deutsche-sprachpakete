import soundfile as sf
import numpy as np
import os

samples_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples"
out_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_cuts"
os.makedirs(out_dir, exist_ok=True)

f02 = os.path.join(samples_dir, "02_Folge 21 Rubble der Fundhund_Kapitel 05 Rubble der Fundhund .mp3")
f03 = os.path.join(samples_dir, "03_Folge 21 Rubble der Fundhund_Kapitel 04 Rubble der Fundhund .mp3")
f00 = os.path.join(samples_dir, "00_Folge 21 Rubble der Fundhund_Kapitel 02 Rubble der Fundhund .mp3")
f01 = os.path.join(samples_dir, "01_Folge 21 Rubble der Fundhund_Kapitel 03 Rubble der Fundhund .mp3")

# Segment 1: f02 from 8.50s to 12.50s ("Ja und wie! Tolles Auto! Danke, dass du mich mitgenommen hast!")
d02, sr = sf.read(f02)
seg1 = d02[int(8.50 * sr):int(12.50 * sr)]

# Segment 2: f03 from 13.40s to 15.60s ("Ich buddel total gern!")
d03, sr3 = sf.read(f03)
seg2 = d03[int(13.40 * sr3):int(15.60 * sr3)]

# Segment 3: f00 from 24.80s to 27.50s ("Ich verspreche, ich bin vorsichtig!")
d00, sr0 = sf.read(f00)
seg3 = d00[int(24.80 * sr0):int(27.50 * sr0)]

# Segment 4: f01 from 4.20s to 7.80s ("Aber das macht mir nichts aus, wirklich nicht!")
d01, sr1 = sf.read(f01)
seg4 = d01[int(4.20 * sr1):int(7.80 * sr1)]

segments = [seg1, seg2, seg3, seg4]
mono_segs = []
for seg in segments:
    if seg.ndim > 1:
        m = np.mean(seg, axis=1)
    else:
        m = seg
    peak = np.max(np.abs(m))
    if peak > 0:
        m = m / peak * 0.90
    mono_segs.append(m)

# Interleave with 0.4s silence
silence = np.zeros(int(0.4 * sr))
combined = np.concatenate([
    mono_segs[0], silence,
    mono_segs[1], silence,
    mono_segs[2], silence,
    mono_segs[3]
])

out_wav = os.path.join(out_dir, "rubble_german_clean.wav")
sf.write(out_wav, combined, sr)

dur = len(combined) / sr
print(f"Clean Rubble training audio created: {out_wav}")
print(f"Duration: {dur:.2f} seconds at {sr} Hz")
