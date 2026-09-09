html_content = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Waze Stimmen-Auswahl: SpongeBob Schwammkopf & Thaddäus Tentakel</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #06101e;
      --card-bg: rgba(13, 27, 46, 0.75);
      --card-border: rgba(56, 189, 248, 0.15);
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --accent-yellow: #facc15;
      --accent-cyan: #06b6d4;
      --accent-red: #ef4444;
      --accent-green: #10b981;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      background-image: 
        radial-gradient(at 0% 0%, rgba(6, 182, 212, 0.18) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(250, 204, 21, 0.12) 0px, transparent 50%),
        radial-gradient(at 50% 50%, rgba(239, 68, 68, 0.1) 0px, transparent 50%);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 40px 20px;
      min-height: 100vh;
    }
    .container {
      max-width: 1300px;
      margin: 0 auto;
    }
    header {
      text-align: center;
      margin-bottom: 35px;
    }
    .badge-top {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(6, 182, 212, 0.15);
      border: 1px solid rgba(6, 182, 212, 0.35);
      color: #38bdf8;
      font-weight: 700;
      font-size: 13px;
      padding: 6px 14px;
      border-radius: 9999px;
      margin-bottom: 16px;
    }
    h1 {
      font-family: 'Outfit', sans-serif;
      font-size: clamp(30px, 4.5vw, 46px);
      font-weight: 800;
      background: linear-gradient(135deg, #38bdf8 0%, #facc15 50%, #f87171 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }
    .subtitle {
      color: var(--text-muted);
      font-size: 16.5px;
      max-width: 820px;
      margin: 0 auto;
      line-height: 1.6;
    }

    /* Training Highlight Banner */
    .train-alert {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15));
      border: 1px solid rgba(16, 185, 129, 0.4);
      border-radius: 14px;
      padding: 16px 22px;
      margin-bottom: 30px;
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .train-alert-icon { font-size: 28px; }
    .train-alert-text { font-size: 14px; line-height: 1.5; color: #e2e8f0; }
    .train-alert-text strong { color: #34d399; }

    /* Selection Banner */
    .selection-banner {
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid rgba(56, 189, 248, 0.3);
      backdrop-filter: blur(14px);
      padding: 18px 24px;
      border-radius: 16px;
      margin-bottom: 40px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      position: sticky;
      top: 20px;
      z-index: 100;
      box-shadow: 0 10px 35px rgba(0,0,0,0.6);
    }
    .selection-items {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }
    .sel-chip {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 8px 14px;
      border-radius: 10px;
      font-size: 13.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .sel-chip strong {
      color: #38bdf8;
    }
    .copy-btn {
      background: linear-gradient(135deg, #0284c7, #0369a1);
      border: none;
      color: white;
      font-weight: 700;
      padding: 10px 20px;
      border-radius: 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      transition: all 0.2s;
    }
    .copy-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
    }

    /* Category Section */
    .category-section {
      margin-bottom: 60px;
    }
    .cat-header {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 24px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .cat-icon {
      font-size: 34px;
      line-height: 1;
    }
    .cat-title {
      font-family: 'Outfit', sans-serif;
      font-size: 28px;
      font-weight: 700;
    }
    .cat-desc {
      color: var(--text-muted);
      font-size: 14.5px;
      margin-left: auto;
    }

    /* Grid of Cards */
    .models-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 22px;
    }
    .model-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 22px;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex;
      flex-direction: column;
      position: relative;
      backdrop-filter: blur(8px);
    }
    .model-card:hover {
      transform: translateY(-3px);
      border-color: rgba(56, 189, 248, 0.4);
      box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
    }
    .model-card.selected {
      border-color: #38bdf8;
      background: rgba(14, 116, 144, 0.2);
      box-shadow: 0 0 28px rgba(6, 182, 212, 0.3);
    }
    .model-card.selected.rage {
      border-color: #ef4444;
      background: rgba(185, 28, 28, 0.2);
      box-shadow: 0 0 28px rgba(239, 68, 68, 0.3);
    }
    .card-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 16px;
      gap: 12px;
    }
    .card-title-group h3 {
      font-family: 'Outfit', sans-serif;
      font-size: 18px;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 4px;
      line-height: 1.3;
    }
    .model-id {
      font-size: 11.5px;
      color: var(--text-muted);
      font-family: monospace;
    }
    .model-tag {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.08);
      color: #94a3b8;
      white-space: nowrap;
    }
    .model-tag.favorit {
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.5);
    }
    .model-tag.rage {
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.5);
    }

    /* Sample Box */
    .sample-box {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 12px;
    }
    .sample-label {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      font-weight: 700;
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
    }
    .sample-text {
      font-size: 12.5px;
      line-height: 1.45;
      color: #cbd5e1;
      font-style: italic;
      margin-bottom: 10px;
    }
    .audio-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .play-btn {
      background: rgba(56, 189, 248, 0.18);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #38bdf8;
      width: 38px;
      height: 38px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s;
      flex-shrink: 0;
    }
    .play-btn:hover {
      background: #0284c7;
      color: #ffffff;
      transform: scale(1.08);
    }
    .play-btn.rage-btn {
      background: rgba(239, 68, 68, 0.2);
      border-color: rgba(239, 68, 68, 0.5);
      color: #f87171;
    }
    .play-btn.rage-btn:hover {
      background: #dc2626;
      color: #ffffff;
    }
    .play-btn svg {
      width: 15px;
      height: 15px;
      fill: currentColor;
    }
    .track-bar {
      flex: 1;
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      position: relative;
      cursor: pointer;
      overflow: hidden;
    }
    .track-fill {
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 0%;
      background: #38bdf8;
      border-radius: 3px;
      transition: width 0.1s linear;
    }
    .track-fill.rage-fill {
      background: #ef4444;
    }
    .track-time {
      font-size: 11px;
      font-family: monospace;
      color: var(--text-muted);
      min-width: 32px;
      text-align: right;
    }

    /* Vote button */
    .vote-btn {
      width: 100%;
      margin-top: 14px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      color: var(--text);
      font-weight: 600;
      font-size: 13.5px;
      padding: 10px 16px;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    .vote-btn:hover {
      background: rgba(255, 255, 255, 0.1);
    }
    .model-card.selected .vote-btn {
      background: linear-gradient(135deg, #0284c7, #0369a1);
      color: white;
      border: none;
      font-weight: 700;
    }
    .model-card.selected.rage .vote-btn {
      background: linear-gradient(135deg, #dc2626, #b91c1c);
      color: white;
      border: none;
      font-weight: 700;
    }

    footer {
      text-align: center;
      padding: 40px 0 20px;
      color: var(--text-muted);
      font-size: 13px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      margin-top: 40px;
    }
  </style>
</head>
<body>

<div class="container">
  <header>
    <div class="badge-top">
      <span>🫧</span> BIKINI BOTTOM SOUNDPACK STUDIO
    </div>
    <h1>SpongeBob Schwammkopf & Thaddäus Tentakel</h1>
    <p class="subtitle">Wähle deinen Favoriten für SpongeBob sowie für Thaddäus (1x Kinderfreundlich & 1x Rage Modus). Klicke auf Play zum Vorhören!</p>
  </header>

  <!-- Training Alert -->
  <div class="train-alert">
    <div class="train-alert-icon">✨</div>
    <div class="train-alert-text">
      <strong>Neu trainiert mit deutscher Original-Synchro:</strong> Wir haben für SpongeBob (Santiago Ziesmer) und Thaddäus (Eberhard Prüter – 1x Kinderfreundlich & 1x Rage) neue KI-Modelle direkt aus den originalen deutschen Tonspuren trainiert!
    </div>
  </div>

  <!-- Sticky Selection Summary -->
  <div class="selection-banner">
    <div>
      <div style="font-size: 12px; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 6px;">Deine gewählten Favoriten:</div>
      <div class="selection-items" id="summaryChips">
        <div class="sel-chip" id="chip-spongebob">🧽 SpongeBob: <strong>Neu trainiert: Deutsche Originalstimme</strong></div>
        <div class="sel-chip" id="chip-thaddaeus_kind">🎶 Thaddäus (Kinderfreundlich): <strong>Neu trainiert: Deutsche Originalstimme</strong></div>
        <div class="sel-chip" id="chip-thaddaeus_rage">💢 Thaddäus (Rage): <strong>Neu trainiert: Original Megaphon Rage</strong></div>
      </div>
    </div>
    <button class="copy-btn" onclick="copySelection()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
      Auswahl kopieren
    </button>
  </div>

  <!-- 1. SPONGEBOB -->
  <section class="category-section" id="sec-spongebob">
    <div class="cat-header">
      <span class="cat-icon">🧽</span>
      <h2 class="cat-title">SpongeBob Schwammkopf</h2>
      <span class="cat-desc">Optimistisch, fröhlich, Quallenfischen & legendäre Lache</span>
    </div>
    <div class="models-grid">
      <!-- SpongeBob Neu Trainiert (Favorit) -->
      <div class="model-card selected" id="card-spongebob_trained" data-cat="spongebob" data-name="Neu trainiert: Deutsche Originalstimme (Santiago Ziesmer)">
        <div class="card-top">
          <div class="card-title-group">
            <h3>🔥 Neu trainiert: Deutsche Originalstimme</h3>
            <div class="model-id">ID: 01f717b1...52ff • Santiago Ziesmer</div>
          </div>
          <span class="model-tag favorit">Original-Synchro</span>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>1. Fahrtantritt</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Hahahahaha! Ich bin bereit, ich bin bereit, ich bin bereit! Schnall dich an, Kumpel! Wir machen heute die Straßen von Bikini Bottom unsicher! Abfahrt!“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('spongebob_trained_start.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>2. Blitzer-Warnung</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Wooohoo! Langsamer, fahr langsamer! Da vorne steht ein Blitzer! Wenn Mrs. Puff das sieht, krieg ich meinen Führerschein nie!“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('spongebob_trained_blitzer.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <button class="vote-btn" onclick="selectModel('spongebob', 'spongebob_trained', 'Neu trainiert: Deutsche Originalstimme (Santiago Ziesmer)')">✓ Als Favorit gewählt</button>
      </div>

      <!-- SpongeBob Modell 1 (Community) -->
      <div class="model-card" id="card-spongebob_mod1" data-cat="spongebob" data-name="Vorheriges Community-Modell (5ea97971)">
        <div class="card-top">
          <div class="card-title-group">
            <h3>Community-Modell 1</h3>
            <div class="model-id">ID: 5ea97971...4011</div>
          </div>
          <span class="model-tag">Community</span>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>1. Fahrtantritt</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Hahahahaha! Ich bin bereit, ich bin bereit, ich bin bereit! Schnall dich an, Kumpel! Wir machen heute die Straßen von Bikini Bottom unsicher! Abfahrt!“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('spongebob_mod1_start.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>2. Blitzer-Warnung</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Wooohoo! Langsamer, fahr langsamer! Da vorne steht ein Blitzer! Wenn Mrs. Puff das sieht, krieg ich meinen Führerschein nie!“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('spongebob_mod1_blitzer.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <button class="vote-btn" onclick="selectModel('spongebob', 'spongebob_mod1', 'Vorheriges Community-Modell (5ea97971)')">Diesen Favoriten wählen</button>
      </div>
    </div>
  </section>

  <!-- 2. THADDÄUS KINDERFREUNDLICH -->
  <section class="category-section" id="sec-thaddaeus_kind">
    <div class="cat-header">
      <span class="cat-icon">🎶</span>
      <h2 class="cat-title">Thaddäus Q. Tentakel (Kinderfreundlich)</h2>
      <span class="cat-desc">Ruhig, sarkastisch, Klarinette üben & genervter Nachbar</span>
    </div>
    <div class="models-grid">
      <!-- Modell Neu Trainiert (Favorit) -->
      <div class="model-card selected" id="card-thaddaeus_kind_trained" data-cat="thaddaeus_kind" data-name="Neu trainiert: Deutsche Originalstimme (Eberhard Prüter)">
        <div class="card-top">
          <div class="card-title-group">
            <h3>🔥 Neu trainiert: Deutsche Originalstimme</h3>
            <div class="model-id">ID: 8d1e3f20...9c98 • Eberhard Prüter</div>
          </div>
          <span class="model-tag favorit">Original-Synchro</span>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>1. Fahrtantritt</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Seufz... Muss das denn wirklich sein? Na schön. Zünd den Motor an und fahr einfach ganz ruhig los, damit ich in Ruhe meine Klarinette üben kann.“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('thaddaeus_kind_trained_start.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>2. Blitzer-Warnung</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Achtung. Da vorne steht ein Blitzer. Brems gefälligst ab, ich habe keine Lust, mein hart verdientes Geld an die Stadt zu verschwenden.“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('thaddaeus_kind_trained_blitzer.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <button class="vote-btn" onclick="selectModel('thaddaeus_kind', 'thaddaeus_kind_trained', 'Neu trainiert: Deutsche Originalstimme (Eberhard Prüter)')">✓ Als Favorit gewählt</button>
      </div>

      <!-- Modell 1 Kinderfreundlich Community -->
      <div class="model-card" id="card-thaddaeus_kind_mod1" data-cat="thaddaeus_kind" data-name="Vorheriges Community-Modell 1 (ca2fc5c4)">
        <div class="card-top">
          <div class="card-title-group">
            <h3>Community-Modell 1</h3>
            <div class="model-id">ID: ca2fc5c4...f712</div>
          </div>
          <span class="model-tag">Community</span>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>1. Fahrtantritt</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Seufz... Muss das denn wirklich sein? Na schön. Zünd den Motor an und fahr einfach ganz ruhig los, damit ich in Ruhe meine Klarinette üben kann.“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('thaddaeus_kind_mod1_start.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>2. Blitzer-Warnung</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Achtung. Da vorne steht ein Blitzer. Brems gefälligst ab, ich habe keine Lust, mein hart verdientes Geld an die Stadt zu verschwenden.“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('thaddaeus_kind_mod1_blitzer.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <button class="vote-btn" onclick="selectModel('thaddaeus_kind', 'thaddaeus_kind_mod1', 'Vorheriges Community-Modell 1 (ca2fc5c4)')">Diesen Favoriten wählen</button>
      </div>

      <!-- Modell 2 Kinderfreundlich Community -->
      <div class="model-card" id="card-thaddaeus_kind_mod2" data-cat="thaddaeus_kind" data-name="Vorheriges Community-Modell 2 (c4a08c39)">
        <div class="card-top">
          <div class="card-title-group">
            <h3>Community-Modell 2</h3>
            <div class="model-id">ID: c4a08c39...ec09</div>
          </div>
          <span class="model-tag">Community</span>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>1. Fahrtantritt</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Seufz... Guten Tag. Bitte fahr einfach ordentlich und ohne alberne Witze. Ich möchte einfach nur pünktlich ankommen.“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('thaddaeus_kind_mod2_start.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>2. Blitzer-Warnung</span><span>Audio-Sample</span></div>
          <div class="sample-text">„Pass mal auf da vorne. Da steht ein Blitzer. Schön das Tempolimit einhalten, sonst gibt's ein Bußgeld.“</div>
          <div class="audio-row">
            <button class="play-btn" onclick="togglePlay('thaddaeus_kind_mod2_blitzer.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <button class="vote-btn" onclick="selectModel('thaddaeus_kind', 'thaddaeus_kind_mod2', 'Vorheriges Community-Modell 2 (c4a08c39)')">Diesen Favoriten wählen</button>
      </div>
    </div>
  </section>

  <!-- 3. THADDÄUS RAGE MODUS -->
  <section class="category-section" id="sec-thaddaeus_rage">
    <div class="cat-header">
      <span class="cat-icon">💢</span>
      <h2 class="cat-title" style="color: #f87171;">Thaddäus Q. Tentakel (Rage Modus)</h2>
      <span class="cat-desc">Brüllen, Wutanfall, komplett die Nerven verlieren</span>
    </div>
    <div class="models-grid">
      <!-- Modell Neu Trainiert Rage (Favorit) -->
      <div class="model-card selected rage" id="card-thaddaeus_rage_trained" data-cat="thaddaeus_rage" data-name="Neu trainiert: Deutsche Originalstimme (Eberhard Prüter - Rage)">
        <div class="card-top">
          <div class="card-title-group">
            <h3 style="color: #fca5a5;">🔥 Neu trainiert: Original Megaphon Rage</h3>
            <div class="model-id">ID: 0f256abe...2f3a • Eberhard Prüter</div>
          </div>
          <span class="model-tag rage">Megaphon Rage</span>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>1. Fahrtantritt</span><span>Audio-Sample</span></div>
          <div class="sample-text">„SPONGEBOB! Hör auf zu lachen und fahr endlich los! Schnall dich an, du Hohlkopf! Ich will einfach nur nach Hause in mein Bett! GIB JETZT ENDLICH GAS!“</div>
          <div class="audio-row">
            <button class="play-btn rage-btn" onclick="togglePlay('thaddaeus_rage_trained_start.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill rage-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>2. Blitzer-Warnung</span><span>Audio-Sample</span></div>
          <div class="sample-text">„BIST DU DENN VÖLLIG WAHNSINNIG?! TRITT AUF DIE BREMSE! DA STEHT EIN BLITZER! Du bringst uns noch alle ins Grab, du Idiot!“</div>
          <div class="audio-row">
            <button class="play-btn rage-btn" onclick="togglePlay('thaddaeus_rage_trained_blitzer.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill rage-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <button class="vote-btn" onclick="selectModel('thaddaeus_rage', 'thaddaeus_rage_trained', 'Neu trainiert: Deutsche Originalstimme (Eberhard Prüter - Rage)')">✓ Als Favorit gewählt</button>
      </div>

      <!-- Modell 1 Rage Community -->
      <div class="model-card rage" id="card-thaddaeus_rage_mod1" data-cat="thaddaeus_rage" data-name="Vorheriges Community-Modell 1 (c4a08c39)">
        <div class="card-top">
          <div class="card-title-group">
            <h3>Community-Modell 1</h3>
            <div class="model-id">ID: c4a08c39...ec09</div>
          </div>
          <span class="model-tag rage">Wutanfall</span>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>1. Fahrtantritt</span><span>Audio-Sample</span></div>
          <div class="sample-text">„SPONGEBOB! Hör auf zu lachen und fahr endlich los! Schnall dich an, du Hohlkopf! Ich will einfach nur nach Hause in mein Bett! GIB JETZT ENDLICH GAS!“</div>
          <div class="audio-row">
            <button class="play-btn rage-btn" onclick="togglePlay('thaddaeus_rage_mod1_start.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill rage-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>2. Blitzer-Warnung</span><span>Audio-Sample</span></div>
          <div class="sample-text">„BIST DU DENN VÖLLIG WAHNSINNIG?! TRITT AUF DIE BREMSE! DA STEHT EIN BLITZER! Du bringst uns noch alle ins Grab, du Idiot!“</div>
          <div class="audio-row">
            <button class="play-btn rage-btn" onclick="togglePlay('thaddaeus_rage_mod1_blitzer.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill rage-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <button class="vote-btn" onclick="selectModel('thaddaeus_rage', 'thaddaeus_rage_mod1', 'Vorheriges Community-Modell 1 (c4a08c39)')">Diesen Favoriten wählen</button>
      </div>

      <!-- Modell 2 Rage Community -->
      <div class="model-card rage" id="card-thaddaeus_rage_mod2" data-cat="thaddaeus_rage" data-name="Vorheriges Community-Modell 2 (ca2fc5c4)">
        <div class="card-top">
          <div class="card-title-group">
            <h3>Community-Modell 2</h3>
            <div class="model-id">ID: ca2fc5c4...f712</div>
          </div>
          <span class="model-tag rage">Ausbruch</span>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>1. Fahrtantritt</span><span>Audio-Sample</span></div>
          <div class="sample-text">„ICH HALTE DAS NICHT MEHR AUS! Fahr sofort los und halt die Klappe! Wenn du noch einmal hupst, raste ich komplett aus!“</div>
          <div class="audio-row">
            <button class="play-btn rage-btn" onclick="togglePlay('thaddaeus_rage_mod2_start.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill rage-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <div class="sample-box">
          <div class="sample-label"><span>2. Blitzer-Warnung</span><span>Audio-Sample</span></div>
          <div class="sample-text">„BREMSEN! DA IST EIN BLITZER, DU VOLLPFOSTEN! Willst du deinen Führerschein verlieren oder was?! TRITT AUF DIE BREMSE!“</div>
          <div class="audio-row">
            <button class="play-btn rage-btn" onclick="togglePlay('thaddaeus_rage_mod2_blitzer.mp3', this)"><svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg></button>
            <div class="track-bar" onclick="seekTrack(event, this)"><div class="track-fill rage-fill"></div></div>
            <span class="track-time">0:00</span>
          </div>
        </div>
        <button class="vote-btn" onclick="selectModel('thaddaeus_rage', 'thaddaeus_rage_mod2', 'Vorheriges Community-Modell 2 (ca2fc5c4)')">Diesen Favoriten wählen</button>
      </div>
    </div>
  </section>

  <footer>
    <p>Waze German Voice Community • Bikini Bottom Edition • 44.1 kHz Mono Studio-Mastering</p>
  </footer>
</div>

<script>
  let currentAudio = null;
  let currentBtn = null;
  let currentTrackBar = null;
  let currentTimeDisplay = null;

  const selections = {
    spongebob: "Neu trainiert: Deutsche Originalstimme (Santiago Ziesmer)",
    thaddaeus_kind: "Neu trainiert: Deutsche Originalstimme (Eberhard Prüter)",
    thaddaeus_rage: "Neu trainiert: Deutsche Originalstimme (Eberhard Prüter - Rage)"
  };

  function updateSummaryUI() {
    document.getElementById('chip-spongebob').innerHTML = `🧽 SpongeBob: <strong>${selections.spongebob}</strong>`;
    document.getElementById('chip-thaddaeus_kind').innerHTML = `🎶 Thaddäus (Kinderfreundlich): <strong>${selections.thaddaeus_kind}</strong>`;
    document.getElementById('chip-thaddaeus_rage').innerHTML = `💢 Thaddäus (Rage): <strong>${selections.thaddaeus_rage}</strong>`;
  }

  function selectModel(cat, cardId, modelName) {
    document.querySelectorAll(`.model-card[data-cat="${cat}"]`).forEach(card => {
      card.classList.remove('selected');
      const btn = card.querySelector('.vote-btn');
      if (btn) btn.textContent = 'Diesen Favoriten wählen';
    });
    const targetCard = document.getElementById(`card-${cardId}`);
    if (targetCard) {
      targetCard.classList.add('selected');
      const btn = targetCard.querySelector('.vote-btn');
      if (btn) btn.textContent = '✓ Als Favorit gewählt';
    }
    selections[cat] = modelName;
    updateSummaryUI();
  }

  function copySelection() {
    const text = `SpongeBob = ${selections.spongebob}\\nThaddäus (Kinderfreundlich) = ${selections.thaddaeus_kind}\\nThaddäus (Rage Modus) = ${selections.thaddaeus_rage}`;
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.querySelector('.copy-btn');
      const orig = btn.innerHTML;
      btn.innerHTML = `✓ In die Zwischenablage kopiert!`;
      btn.style.background = '#10b981';
      setTimeout(() => {
        btn.innerHTML = orig;
        btn.style.background = '';
      }, 2500);
    });
  }

  function togglePlay(src, btn) {
    const trackBar = btn.parentElement.querySelector('.track-bar');
    const timeDisplay = btn.parentElement.querySelector('.track-time');
    const fill = trackBar.querySelector('.track-fill');

    if (currentAudio && currentAudio.dataset.src === src) {
      if (!currentAudio.paused) {
        currentAudio.pause();
        btn.innerHTML = `<svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>`;
      } else {
        currentAudio.play();
        btn.innerHTML = `<svg viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`;
      }
      return;
    }

    if (currentAudio) {
      currentAudio.pause();
      if (currentBtn) currentBtn.innerHTML = `<svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>`;
      if (currentTrackBar) currentTrackBar.querySelector('.track-fill').style.width = '0%';
    }

    currentAudio = new Audio(src);
    currentAudio.dataset.src = src;
    currentBtn = btn;
    currentTrackBar = trackBar;
    currentTimeDisplay = timeDisplay;

    btn.innerHTML = `<svg viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`;

    currentAudio.ontimeupdate = () => {
      if (!currentAudio.duration) return;
      const pct = (currentAudio.currentTime / currentAudio.duration) * 100;
      fill.style.width = pct + '%';
      const m = Math.floor(currentAudio.currentTime / 60);
      const s = Math.floor(currentAudio.currentTime % 60).toString().padStart(2, '0');
      timeDisplay.textContent = `${m}:${s}`;
    };

    currentAudio.onended = () => {
      btn.innerHTML = `<svg viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>`;
      fill.style.width = '0%';
      timeDisplay.textContent = '0:00';
    };

    currentAudio.play();
  }

  function seekTrack(event, bar) {
    if (!currentAudio) return;
    const rect = bar.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const pct = clickX / rect.width;
    if (currentAudio.duration) {
      currentAudio.currentTime = pct * currentAudio.duration;
    }
  }

  updateSummaryUI();
</script>
</body>
</html>
"""

with open(r"c:\Users\PC\Desktop\Waze German Voice\packs\Samples_BikiniBottom\vergleich.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated vergleich.html successfully!")
