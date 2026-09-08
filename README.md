# 🇩🇪 Waze Deutsche Voicepacks & KI-Stimmen (German Voicepack Links)

[![Waze Supported](https://img.shields.io/badge/Waze-iOS%20%7C%20Android-33ccff?style=for-the-badge&logo=waze&logoColor=white)](https://www.waze.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Lokasorn/waze-deutsche-sprachpakete?style=for-the-badge&color=gold)](https://github.com/Lokasorn/waze-deutsche-sprachpakete)
[![Community](https://img.shields.io/badge/Community-Deutsche%20Waze%20Stimmen-blueviolet?style=for-the-badge)](https://github.com/Lokasorn/waze-deutsche-sprachpakete)

Eine offene Community-Sammlung von individuellen **deutschen Waze-Sprachpaketen** mit KI-trainierten Stimmen von bekannten **YouTubern, Streamern, Memes und Charakteren**.

> 💡 **So funktioniert's:** Öffne diese Seite auf deinem Smartphone (iOS oder Android) und tippe einfach auf den **Waze-Installationslink**. Die Waze-App öffnet sich automatisch und lädt die Stimme direkt herunter!

---

## 🎙️ Verfügbare Deutsche Sprachpakete

| Stimme / Charakter | Kategorie | 1-Klick Waze Link | Beispiel-Ansage | Größe | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| 👑 **MontanaBlack (Monte)** | Streamer / Gaming | [👉 **In Waze installieren**](https://waze.com/ul?acvp=ba4b303a-afe8-4475-8853-afb610137172) | *"Rein in die Olga, ab geht die wilde Fahrt!"* | 0.47 MB | 🟢 Aktiv |
| 🚗 **Standard Deutsch (Neural)** | Navigation / Klar | [👉 **In Waze installieren**](https://waze.com/ul?acvp=standard-de-voice) *(In Kürze)* | *"Alles bereit. Gute und sichere Fahrt!"* | 0.58 MB | 🟡 Bereit |

> *Möchtest du weitere Stimmen wie Papaplatte, Knossi oder Gronkh hinzufügen? Siehe [Mitwirken / Eigene Stimmen erstellen](#-eigene-stimmen-erstellen).*

---

## 📱 Installationsanleitung (Smartphone)

### Auf iPhone & Android:
1. Vergewissere dich, dass die **Waze-App** auf deinem Smartphone installiert ist.
2. Tippe in der Tabelle oben auf den Link **"In Waze installieren"** (oder kopiere den Link):
   ```text
   https://waze.com/ul?acvp=ba4b303a-afe8-4475-8853-afb610137172
   ```
3. Waze öffnet sich automatisch mit dem Dialog:
   > *"Möchtest du dieses Sprachpaket herunterladen?"*
4. Tippe auf **Herunterladen** (Download).
5. Fertig! Die Stimme ist ab sofort in **Einstellungen → Stimme & Sound → Waze-Stimme** aktiv.

---

## 🎧 Enthaltene Ansagen im MontanaBlack-Pack (43 Prompts)

Das MontanaBlack-Sprachpaket deckt alle 43 Kernbefehle von Waze ab:

- **Start der Fahrt**:
  - *"Jo Freunde, Monte hier! Rein in die Olga, ab geht die wilde Fahrt!"*
  - *"Uff jeden! Navi steht, jetzt aber keine Mätzchen auf der Bahn!"*
  - *"Geisteskrank! Route ist geladen, zieh durch!"*
- **Blitzer & Polizei**:
  - 🚨 **Polizei**: *"Achtung Digger! Die Cops campen da vorne! Schön brav 50 fahren!"*
  - 📸 **Fester Blitzer**: *"Blitzer voraus! Geh sofort vom Gas, dein Kontostand weint sonst!"*
  - 🚦 **Ampelblitzer**: *"Ampelblitzer! Nicht bei Gelb rüberdrücken, bist du irre?!"*
- **Verkehr & Stau**:
  - 🚗 **Stau**: *"Stau voraus... Digga ich raste komplett aus! Wer steht da wieder?!"*
  - ⚠️ **Unfall**: *"Unfall voraus gemeldet! Fahr vorsichtig vorbei und gaff nicht!"*
- **Manöver & Richtungen**:
  - ↩️ **Wenden**: *"Bruder, komplett lost! Sofort umdrehen!"*
  - 🏁 **Ziel erreicht**: *"Ziel erreicht! Ez win, Bruder! Endlich raus hier!"*

---

## 🛠️ Eigene Stimmen erstellen & hochladen

In diesem Repository sind alle Skripte enthalten, um mit einem einzigen Befehl ein neues deutsches Soundpack zu trainieren, abzumischen und auf die Waze-Server hochzuladen:

```bash
# 1. MontanaBlack Pack neu bauen / aktualisieren:
python tools/build_montanablack_pack.py

# 2. Direkt zu Waze hochladen & neuen acvp-Link generieren:
python tools/upload_montanablack.py
```

### Automatische Optimierungen:
- **Mono-Konvertierung & 44.1 kHz**: Optimiert für KFZ-Lautsprecher.
- **Lautstärke-Boost (+7 dB)**: Klare Verständlichkeit gegen Fahrgeräusche und Musik.
- **Auto-Kompression (< 0.79 MB)**: Hält Wazes strenges 0.8 MB Server-Limit deterministisch ein.

---

## ❓ Häufig gestellte Fragen (FAQ)

#### Sagt die Stimme auch Straßennamen an?
Nein. Wie bei allen Custom-Voicepacks in Waze (auch bei offiziellen Promi-Stimmen wie Terminator oder Arnold Schwarzenegger) werden nur die 43 Standard-Navigationsbefehle gesprochen. Dynamische Straßennamen werden ausschließlich von den Standard-Systemstimmen unterstützt.

#### Was tun, wenn der Link Waze nicht öffnet?
Kopiere den Link `https://waze.com/ul?acvp=...` und sende ihn dir z. B. per WhatsApp, Telegram oder Notizen auf dein Smartphone, und tippe dort darauf.

---

## 🤝 Mitwirken (Contributing)

Du hast eine eigene deutsche Stimme erstellt oder möchtest eine YouTuber-Stimme beisteuern?
1. Forke dieses Repository.
2. Füge dein MP3-Paket in `packs/<Name>/` ein.
3. Trage deinen Link in `helper_files/waze_vps.json` und die Tabelle in `README.md` ein.
4. Erstelle einen Pull Request!
