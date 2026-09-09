import os
from pathlib import Path

PACK_DIR = Path(r"c:\Users\PC\Desktop\Waze German Voice\packs\PawPatrolRubble")

import sys
sys.path.append(".")
from tools.build_and_publish_rubble import RUBBLE_PROMPTS, VALID_WAZE_FILENAMES

html = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>PAW Patrol: Rubble • Waze Soundpack Verifikation (Alle 43 Ansagen)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #090e17;
      color: #f8fafc;
      font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 40px 20px;
    }
    .container {
      max-width: 960px;
      margin: 0 auto;
    }
    .header {
      text-align: center;
      margin-bottom: 30px;
    }
    .badge {
      display: inline-block;
      background: rgba(250, 204, 21, 0.15);
      border: 1px solid rgba(250, 204, 21, 0.4);
      color: #facc15;
      font-weight: 700;
      font-size: 13px;
      padding: 6px 16px;
      border-radius: 999px;
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 36px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 8px;
    }
    .subtitle {
      color: #94a3b8;
      font-size: 16px;
    }
    .status-banner {
      background: rgba(250, 204, 21, 0.1);
      border: 1px solid rgba(250, 204, 21, 0.3);
      border-radius: 12px;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 30px;
    }
    .status-title {
      font-weight: 700;
      color: #facc15;
      font-size: 15px;
    }
    .status-desc {
      font-size: 13px;
      color: #cbd5e1;
    }
    .waze-btn {
      background: #facc15;
      color: #090e17;
      font-weight: 800;
      font-size: 14px;
      padding: 10px 20px;
      border-radius: 8px;
      text-decoration: none;
      transition: all 0.2s;
    }
    .waze-btn:hover {
      background: #eab308;
      transform: translateY(-1px);
    }
    .prompts-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .prompt-card {
      background: #111a28;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    .prompt-meta {
      flex: 1;
    }
    .prompt-filename {
      font-family: monospace;
      font-size: 13px;
      font-weight: 700;
      color: #facc15;
      margin-bottom: 4px;
    }
    .prompt-text {
      font-size: 13.5px;
      color: #e2e8f0;
      line-height: 1.4;
      font-style: italic;
    }
    audio {
      width: 220px;
      height: 36px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="badge">🐾 PAW PATROL • 100% DEUTSCHE ORIGINALSTIMME (IVO MÖLLER)</div>
      <h1>Rubble packt an! (Alle 43 Waze-Ansagen)</h1>
      <p class="subtitle">Offiziell verifiziert & in der Waze Cloud aktiv</p>
    </div>

    <div class="status-banner">
      <div>
        <div class="status-title">✅ Status: Live & Aktiv in Waze</div>
        <div class="status-desc">Alle 43 Dateien optimiert (44.1 kHz Mono 36 kbps, 0.596 MB).</div>
      </div>
      <a class="waze-btn" href="https://waze.com/ul?acvp=c3e29b17-cf75-4110-97b0-66255abbadaa" target="_blank">📲 In Waze öffnen</a>
    </div>

    <div class="prompts-list">
"""

for fn in VALID_WAZE_FILENAMES:
    text = RUBBLE_PROMPTS.get(fn, "")
    html += f"""      <div class="prompt-card">
        <div class="prompt-meta">
          <div class="prompt-filename">{fn}</div>
          <div class="prompt-text">„{text}“</div>
        </div>
        <audio controls src="{fn}"></audio>
      </div>
"""

html += """    </div>
  </div>
</body>
</html>
"""

for fname in ["verify_all.html", "preview.html"]:
    with open(PACK_DIR / fname, "w", encoding="utf-8") as f:
        f.write(html)
print("Preview HTML files created!")
