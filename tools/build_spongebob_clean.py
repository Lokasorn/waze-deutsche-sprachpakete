import soundfile as sf
import numpy as np

f_pizza = r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples\05_Folge 3 Das Original-Hörspiel zur TV-Serie_Pizza-Heimservice.mp3"
f_kekse = r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_samples_more\00_Folge_275__Die_Keks-_Kapitel_01_-_Die_Kek.mp3"
dst = r"c:\Users\PC\Desktop\Waze German Voice\tools\spongebob_clean_voice.wav"

data_pizza, sr_pizza = sf.read(f_pizza)
data_kekse, sr_kekse = sf.read(f_kekse)

# Segment 1: Pizza 0.0s to 7.0s ("Kundschaft geht vor! Ja vielleicht...")
seg1 = data_pizza[0:int(7.0 * sr_pizza)]

# Segment 2: Pizza 12.0s to 22.0s ("Was ist das? Ist das der Käse? Oh ja...")
seg2 = data_pizza[int(12.0 * sr_pizza):int(22.0 * sr_pizza)]

# Segment 3: Kekse 15.8s to 21.0s ("Guten Tag die Damen! Möchten Sie vielleicht...")
# Resample or match if sample rate differs
if sr_kekse != sr_pizza:
    import librosa
    data_kekse = librosa.resample(data_kekse.T if data_kekse.ndim > 1 else data_kekse, orig_sr=sr_kekse, target_sr=sr_pizza).T
    sr_kekse = sr_pizza

seg3 = data_kekse[int(15.8 * sr_kekse):int(21.0 * sr_kekse)]

# Ensure same number of channels (mono)
if seg1.ndim > 1:
    seg1 = np.mean(seg1, axis=1)
if seg2.ndim > 1:
    seg2 = np.mean(seg2, axis=1)
if seg3.ndim > 1:
    seg3 = np.mean(seg3, axis=1)

silence = np.zeros(int(0.25 * sr_pizza))

combined = np.concatenate([seg1, silence, seg2, silence, seg3])
sf.write(dst, combined, sr_pizza)

dur = len(combined) / sr_pizza
print(f"Created SpongeBob Clean Voice: {dur:.2f}s -> {dst}")
