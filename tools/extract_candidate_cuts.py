import soundfile as sf
import os
import numpy as np

out_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_cuts"
os.makedirs(out_dir, exist_ok=True)

samples_dir = r"c:\Users\PC\Desktop\Waze German Voice\tools\rubble_samples"

# Clip 1: from 02_Folge 21 (8.0s to 13.5s) -> "Ja und wie! Tolles Auto! Danke, dass du mich mitgenommen hast!"
f02 = os.path.join(samples_dir, "02_Folge 21 Rubble der Fundhund_Kapitel 05 Rubble der Fundhund .mp3")
d02, sr = sf.read(f02)
c1 = d02[int(8.0 * sr):int(13.5 * sr)]
sf.write(os.path.join(out_dir, "clip1_tolles_auto.wav"), c1, sr)

# Clip 2: from 00_Folge 21 (16.0s to 21.0s) -> "Du hast ja eine tolle Ausrüstung und so ein tolles Netz, danke!"
f00 = os.path.join(samples_dir, "00_Folge 21 Rubble der Fundhund_Kapitel 02 Rubble der Fundhund .mp3")
d00, sr = sf.read(f00)
c2 = d00[int(16.0 * sr):int(21.0 * sr)]
sf.write(os.path.join(out_dir, "clip2_tolle_ausruestung.wav"), c2, sr)

# Clip 3: from 00_Folge 21 (24.0s to 27.5s) -> "Ich verspreche ich bin vorsichtig!"
c3 = d00[int(24.0 * sr):int(27.5 * sr)]
sf.write(os.path.join(out_dir, "clip3_vorsichtig.wav"), c3, sr)

# Clip 4: from 01_Folge 21 (3.5s to 8.5s) -> "Aber das macht mir nichts aus, wirklich nicht!"
f01 = os.path.join(samples_dir, "01_Folge 21 Rubble der Fundhund_Kapitel 03 Rubble der Fundhund .mp3")
d01, sr = sf.read(f01)
c4 = d01[int(3.5 * sr):int(8.5 * sr)]
sf.write(os.path.join(out_dir, "clip4_macht_nichts_aus.wav"), c4, sr)

print("Extracted clips successfully!")
for name in ["clip1_tolles_auto.wav", "clip2_tolle_ausruestung.wav", "clip3_vorsichtig.wav", "clip4_macht_nichts_aus.wav"]:
    p = os.path.join(out_dir, name)
    d, s = sf.read(p)
    print(f"{name}: {len(d)/s:.2f}s, max_amplitude: {np.max(np.abs(d)):.3f}")
