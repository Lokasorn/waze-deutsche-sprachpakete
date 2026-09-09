import json
import re
from pathlib import Path

WORKSPACE_DIR = Path(r"c:\Users\PC\Desktop\Waze German Voice")
VPS_JSON_PATH = WORKSPACE_DIR / "helper_files" / "waze_vps.json"
README_PATH = WORKSPACE_DIR / "README.md"
PUBLISHED_JSON_PATH = WORKSPACE_DIR / "tools" / "published_three_packs.json"

def de_sort_key(name):
    # German DIN 5007-1 alphabetical sort key
    s = name.lower()
    s = s.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    # strip non-alphanumeric at start
    s = re.sub(r'^[^a-z0-9]+', '', s)
    return s

def main():
    if not PUBLISHED_JSON_PATH.exists():
        print(f"Error: {PUBLISHED_JSON_PATH} does not exist yet!")
        return

    with open(PUBLISHED_JSON_PATH, "r", encoding="utf-8") as f:
        new_packs = json.load(f)

    with open(VPS_JSON_PATH, "r", encoding="utf-8") as f:
        all_vps = json.load(f)

    # Convert to dict by slug
    vps_map = {item["slug"]: item for item in all_vps}

    # Update with newly published packs
    for slug, pdata in new_packs.items():
        vps_map[slug] = {
            "name": pdata["name"],
            "slug": pdata["slug"],
            "language": pdata["language"],
            "country_code": pdata["country_code"],
            "category": pdata["category"],
            "waze_link": pdata["waze_link"],
            "download_url": pdata["download_url"],
            "uuid": pdata["uuid"],
            "file_size_mb": pdata["file_size_mb"],
            "prompts_count": 43,
            "status": "Active",
            "author": "German Waze Community",
            "sample_line": pdata["sample_line"]
        }

    # Sort strictly alphabetically by German sort key
    sorted_vps = sorted(vps_map.values(), key=lambda x: de_sort_key(x["name"]))

    with open(VPS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted_vps, f, indent=2, ensure_ascii=False)
    print(f"Updated {VPS_JSON_PATH} with {len(sorted_vps)} total soundpacks (DIN 5007 A-Z)!")

    # Update README.md
    promis = []
    characters = []

    real_slugs = ["angela-merkel", "bastighg", "dieter-bohlen", "drachenlord", "friedrich-merz", "montanablack", "papaplatte", "timgioh"]

    emoji_map = {
        "angela-merkel": "🇩🇪",
        "bastighg": "🌍",
        "dieter-bohlen": "🔥",
        "drachenlord": "👑",
        "friedrich-merz": "🇩🇪",
        "montanablack": "👑",
        "papaplatte": "⚡",
        "timgioh": "🎴",
        "bayrisch": "🥨",
        "beleidigend": "😈",
        "gelangweilt": "🥱",
        "koelsch": "🍺",
        "lustig": "🎉",
        "paw-patrol-rubble": "🐾",
        "saechsisch": "☕",
        "schwaebisch": "🥨",
        "sexy-akzentfrei": "💋",
        "sexy-flirt": "💋",
        "spongebob-schwammkopf": "🧽",
        "thaddaeus-tentakel": "🎶",
        "wuetend": "🤬"
    }

    folder_map = {
        "angela-merkel": "AngelaMerkel",
        "bastighg": "BastiGHG",
        "dieter-bohlen": "DieterBohlen",
        "drachenlord": "Drachenlord",
        "friedrich-merz": "FriedrichMerz",
        "montanablack": "MontanaBlack",
        "papaplatte": "Papaplatte",
        "timgioh": "TimGioh",
        "bayrisch": "Bayrisch",
        "beleidigend": "Beleidigend",
        "gelangweilt": "Gelangweilt",
        "koelsch": "Koelsch",
        "lustig": "Lustig",
        "paw-patrol-rubble": "PawPatrolRubble",
        "saechsisch": "Saechsisch",
        "schwaebisch": "Schwaebisch",
        "sexy-akzentfrei": "SexyAkzentfrei",
        "sexy-flirt": "SexyFlirt",
        "spongebob-schwammkopf": "SpongeBobSchwammkopf",
        "thaddaeus-tentakel": "ThaddaeusTentakel",
        "wuetend": "Wuetend"
    }

    for p in sorted_vps:
        slug = p["slug"]
        if slug in real_slugs:
            promis.append(p)
        else:
            characters.append(p)

    def render_table(pack_list):
        lines = [
            "| Name / Charakter | Kategorie | Waze-Link | MP3-Dateien | Beispiel-Ansage | Größe | Status |",
            "|:---|:---|:---:|:---:|:---|:---:|:---:|",
        ]
        for p in pack_list:
            slug = p["slug"]
            emoji = emoji_map.get(slug, "🎙️")
            name_col = f"{emoji} **{p['name']}**"
            folder = folder_map.get(slug, slug)
            mp3_col = f"[📁 MP3-Ordner](packs/{folder}/) \\| [.tar.gz]({p['download_url']})"
            waze_col = f"[📲 In Waze installieren]({p['waze_link']})"
            sample = p["sample_line"]
            if len(sample) > 70:
                sample = sample[:67] + "..."
            sample_col = f"*\"{sample}\"*"
            size_col = f"{p['file_size_mb']:.2f} MB"
            lines.append(f"| {name_col} | {p['category']} | {waze_col} | {mp3_col} | {sample_col} | {size_col} | 🟢 Aktiv |")
        return "\n".join(lines)

    readme_content = f"""# 🇩🇪 Waze Deutsche Voicepacks (German Voicepack Links)

[![Waze Supported](https://img.shields.io/badge/Waze-iOS%20%7C%20Android-33ccff?style=for-the-badge&logo=waze&logoColor=white)](https://www.waze.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Lokasorn/waze-deutsche-sprachpakete?style=for-the-badge&color=gold)](https://github.com/Lokasorn/waze-deutsche-sprachpakete)
[![Community](https://img.shields.io/badge/Community-Deutsche%20Waze%20Stimmen-blueviolet?style=for-the-badge)](https://github.com/Lokasorn/waze-deutsche-sprachpakete)

Ein von der Community gepflegtes Archiv für individuelle und klassische **deutsche Waze-Navigationsstimmen** – alles an einem zentralen Ort.

Hol dir die Stimmen bekannter deutscher **Streamer, YouTuber, Memes und Charaktere** mit einem Klick direkt in deine Waze-App!

---

## 🚗 Was ist das hier?

Dieses Repository sammelt öffentlich teilbare deutsche Waze-Sprachpakete, damit sie dauerhaft erhalten bleiben und nicht in alten Forenbeiträgen oder toten Social-Media-Links verloren gehen.

Das Ziel dieser Sammlung:
- **Einfach zu finden**: Alle deutschen Sprachpakete übersichtlich gelistet.
- **1-Klick-Installation**: Direkte Waze-Deeplinks für Smartphones (iOS & Android).
- **Direkter Audio-Zugriff**: Alle MP3-Dateien und Pakete direkt zum Anhören und Herunterladen verlinkt.
- **Community-gepflegt**: Jeder kann neue deutsche Sprachpakete einreichen.

---

## 📲 So installierst du ein Sprachpaket (Smartphone)

1. Installiere die offizielle **Waze-App** auf deinem Smartphone (iOS oder Android).
2. Öffne diese GitHub-Seite **auf deinem Smartphone**.
3. Tippe in der Tabelle unten auf den gewünschten **Waze-Link**.
4. Waze öffnet sich automatisch mit der Frage: *"Möchtest du dieses Sprachpaket herunterladen?"*
5. Tippe auf **Herunterladen** – fertig! Die Stimme ist ab sofort in **Einstellungen → Stimme & Sound → Waze-Stimme** aktiv.

---

# 🎙️ Liste der Deutschen Waze-Stimmen

### 🌟 YouTuber, Streamer & Prominente (Echte Personen)
*Alphabetisch sortiert (A–Z)*

{render_table(promis)}

---

### 🎭 Charaktere, Akzente & Fiktive Stimmen
*Alphabetisch sortiert (A–Z)*

{render_table(characters)}

> Weitere Stimmen von Streamern, Dialekten und Charakteren folgen in Kürze durch die Community!

---

## ❓ Häufig gestellte Fragen (FAQ)

#### Sagt die Stimme auch Straßennamen an?
Nein. Wie bei allen Custom-Voicepacks in Waze (auch bei offiziellen Promi-Stimmen wie Arnold Schwarzenegger oder C-3PO) werden ausschließlich die 43 Standard-Navigationsbefehle gesprochen. Dynamische Straßennamen werden nur von den Standard-Systemstimmen unterstützt.

#### Was tun, wenn der Link Waze nicht automatisch öffnet?
Kopiere den Link `https://waze.com/ul?acvp=ba4b303a-afe8-4475-8853-afb610137172` und sende ihn dir z. B. per WhatsApp, Telegram oder Notizen-App auf dein Smartphone und tippe dort direkt darauf.

---

## 🤝 Sprachpaket einreichen / Mitwirken (Contributing)

Du hast ein eigenes deutsches Waze-Soundpack erstellt oder möchtest ein neues Paket beisteuern?
1. Forke dieses Repository.
2. Füge deinen MP3-Ordner unter `packs/<Name>/` ein (muss die 43 Waze-Audiodateien enthalten).
3. Trage deine Stimme in die Tabelle in der `README.md` und in `helper_files/waze_vps.json` ein.
4. Erstelle einen Pull Request!
"""

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Updated {README_PATH} successfully!")

if __name__ == "__main__":
    main()
