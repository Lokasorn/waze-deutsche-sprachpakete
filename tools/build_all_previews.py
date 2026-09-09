import json
from pathlib import Path

WORKSPACE_DIR = Path(r"c:\Users\PC\Desktop\Waze German Voice")

PACKS = [
    {
        "folder": "PawPatrolRubble",
        "title": "PAW Patrol: Rubble",
        "badge": "🐶 PAW PATROL • 100% DEUTSCHE ORIGINALSTIMME (IVO MÖLLER)",
        "desc": "Offizielles Waze Soundpack mit Rubble, dem hilfsbereiten Bauarbeiter-Welpen. Alle 43 Ansagen mit vollem Welpen-Charakter und 'Wau wau!'.",
        "color": "#facc15",
        "link": "https://waze.com/ul?acvp=3f7b9138-3582-4281-8125-2a0e33f59482",
        "tar": "https://voice-prompts-ipv6.waze.com/3f7b9138-3582-4281-8125-2a0e33f59482.tar.gz"
    },
    {
        "folder": "SpongeBobSchwammkopf",
        "title": "SpongeBob Schwammkopf",
        "badge": "🧽 BIKINI BOTTOM • ORIGINAL-SYNCHRO (SANTIAGO ZIESMER)",
        "desc": "Das legendäre Waze Soundpack mit SpongeBob Schwammkopf! Voller Optimismus, ansteckendem Lachen und Krabbenburger-Heißhunger auf allen Straßen.",
        "color": "#facc15",
        "link": "https://waze.com/ul?acvp=d49d8584-89f1-41e3-a944-bdce55653fea",
        "tar": "https://voice-prompts-ipv6.waze.com/d49d8584-89f1-41e3-a944-bdce55653fea.tar.gz"
    },
    {
        "folder": "ThaddaeusTentakel",
        "title": "Thaddäus Tentakel",
        "badge": "🎶 BIKINI BOTTOM • ORIGINAL-SYNCHRO (EBERHARD PRÜTER)",
        "desc": "Das ultimative Soundpack für anspruchsvolle Autofahrer. Thaddäus Q. Tentakel begleitet dich mit feinstem Sarkasmus, Klarinetten-Liebe und trockener Kritik.",
        "color": "#38bdf8",
        "link": "https://waze.com/ul?acvp=3be41812-4f71-443e-8568-91ca21f49c0c",
        "tar": "https://voice-prompts-ipv6.waze.com/3be41812-4f71-443e-8568-91ca21f49c0c.tar.gz"
    }
]

def make_preview_html(p):
    pack_dir = WORKSPACE_DIR / "packs" / p["folder"]
    mp3_files = sorted([f.name for f in pack_dir.glob("*.mp3")])

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>{p['title']} • Waze Soundpack (Alle 43 Ansagen)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #090e17;
      color: #f8fafc;
      font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 40px 20px;
      min-height: 100vh;
    }}
    .container {{
      max-width: 1050px;
      margin: 0 auto;
    }}
    .header {{
      text-align: center;
      margin-bottom: 35px;
    }}
    .badge {{
      display: inline-block;
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.35);
      color: {p['color']};
      font-weight: 700;
      font-size: 13px;
      padding: 6px 16px;
      border-radius: 999px;
      margin-bottom: 14px;
      letter-spacing: 0.04em;
    }}
    h1 {{
      font-family: 'Outfit', sans-serif;
      font-size: 40px;
      font-weight: 800;
      background: linear-gradient(135deg, #ffffff 0%, {p['color']} 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 12px;
    }}
    .desc {{
      color: #94a3b8;
      font-size: 16px;
      max-width: 680px;
      margin: 0 auto 24px;
      line-height: 1.6;
    }}
    .action-bar {{
      display: flex;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
      margin-bottom: 40px;
    }}
    .btn {{
      padding: 12px 24px;
      border-radius: 12px;
      font-weight: 700;
      font-size: 15px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }}
    .btn-waze {{
      background: linear-gradient(135deg, #0284c7, #0369a1);
      color: white;
      box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
    }}
    .btn-waze:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(2, 132, 199, 0.6);
    }}
    .btn-secondary {{
      background: rgba(255, 255, 255, 0.08);
      color: #f1f5f9;
      border: 1px solid rgba(255, 255, 255, 0.15);
    }}
    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.14);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 14px;
      padding: 16px;
      transition: transform 0.2s, border-color 0.2s;
    }}
    .card:hover {{
      transform: translateY(-2px);
      border-color: rgba(56, 189, 248, 0.4);
    }}
    .card-title {{
      font-family: monospace;
      font-size: 13.5px;
      font-weight: 700;
      color: #38bdf8;
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
    }}
    audio {{
      width: 100%;
      height: 36px;
      border-radius: 8px;
    }}
    footer {{
      text-align: center;
      margin-top: 50px;
      padding-top: 24px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      color: #64748b;
      font-size: 13px;
    }}
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="badge">{p['badge']}</div>
    <h1>{p['title']}</h1>
    <p class="desc">{p['desc']}</p>
    <div class="action-bar">
      <a href="{p['link']}" class="btn btn-waze">📲 In Waze aktivieren</a>
      <a href="{p['tar']}" class="btn btn-secondary">💾 Direkt-Download (.tar.gz)</a>
    </div>
  </div>

  <div class="grid">
"""
    for fn in mp3_files:
        html += f"""    <div class="card">
      <div class="card-title"><span>{fn}</span></div>
      <audio controls preload="none" src="{fn}"></audio>
    </div>\n"""

    html += f"""  </div>
  <footer>
    Waze German Voice Community • {p['title']} • 44.1 kHz Mono Studio-Mastering • 43/43 Prompts
  </footer>
</div>
</body>
</html>"""

    with open(pack_dir / "preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Created preview.html for {p['title']}")

for p in PACKS:
    make_preview_html(p)
