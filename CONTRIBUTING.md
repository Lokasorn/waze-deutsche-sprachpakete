# Mitwirken an den Deutschen Waze Voicepacks

Vielen Dank für dein Interesse, neue deutsche Sprachpakete zu diesem Repository beizutragen!

## Kriterien für die Aufnahme
Damit ein deutsches Soundpack aufgenommen wird, muss es folgende Kriterien erfüllen:
1. **Dateiformat & Namen**: Es muss die offiziellen Waze-Dateinamen nutzen (z. B. `StartDrive1.mp3`, `TurnLeft.mp3`, `Police.mp3` etc.).
2. **Dateigröße**: Die Gesamtgröße aller MP3s darf **0.8 MB nicht überschreiten** (Waze-Server-Begrenzung).
3. **Audio-Qualität**: Mono MP3, Lautstärke ausreichend angehoben (+6 bis +7 dB).
4. **Waze-Link**: Das Pack muss erfolgreich zu Waze hochgeladen worden sein und einen funktionierenden `https://waze.com/ul?acvp=...` Link besitzen.

## So reichst du ein Sprachpaket ein:
1. Forke dieses Repository.
2. Füge dein Sprachpaket in den Ordner `packs/<Name_des_Packs>/` ein.
3. Ergänze deinen Eintrag in `helper_files/waze_vps.json`.
4. Füge deine Zeile in die Tabelle der `README.md` ein.
5. Erstelle einen Pull Request mit einer kurzen Beschreibung deines Soundpacks.
