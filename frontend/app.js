/**
 * Waze Voice Studio - Frontend Logic
 * Handles interactive prompt editing, TTS generation, live audio playback,
 * preset switching, ElevenLabs cloning, and Waze Cloud Deep-Link publishing.
 */

const API_BASE = window.location.origin;

// State
let appState = {
  activePackName: null,
  promptsMeta: {},
  presetsMeta: {},
  categories: [],
  validFilenames: [],
  packDetails: null,
  activeCategory: 'all',
  edgeVoices: [],
  elevenlabsVoices: [],
  currentAudio: null,
  currentPlayingFilename: null,
  companionIndex: 0,
};

// DOM Elements
const selectActivePack = document.getElementById('select-active-pack');
const btnRefreshPacks = document.getElementById('btn-refresh-packs');
const btnNewPack = document.getElementById('btn-new-pack');
const statProgressVal = document.getElementById('stat-progress-val');
const statSizeVal = document.getElementById('stat-size-val');
const statStatusText = document.getElementById('stat-status-text');
const statStatusPill = document.getElementById('stat-status-pill');

const btnGenerateAll = document.getElementById('btn-generate-all');
const btnOptimizeSize = document.getElementById('btn-optimize-size');
const btnDownloadZip = document.getElementById('btn-download-zip');
const btnUploadWaze = document.getElementById('btn-upload-waze');

const selectTtsEngine = document.getElementById('select-tts-engine');
const engineBadge = document.getElementById('engine-badge');
const edgeVoiceGroup = document.getElementById('edge-voice-group');
const selectEdgeVoice = document.getElementById('select-edge-voice');
const elevenlabsSettingsGroup = document.getElementById('elevenlabs-settings-group');
const inputElevenlabsApiKey = document.getElementById('input-elevenlabs-api-key');
const btnLoadElevenlabsVoices = document.getElementById('btn-load-elevenlabs-voices');
const selectElevenlabsVoice = document.getElementById('select-elevenlabs-voice');

const selectScriptPreset = document.getElementById('select-script-preset');
const presetBadge = document.getElementById('preset-badge');
const presetDescriptionText = document.getElementById('preset-description-text');
const btnApplyPreset = document.getElementById('btn-apply-preset');

const categoryTabs = document.getElementById('category-tabs');
const promptsContainer = document.getElementById('prompts-container');
const batchProgressContainer = document.getElementById('batch-progress-container');
const batchProgressFill = document.getElementById('batch-progress-fill');
const batchProgressCount = document.getElementById('batch-progress-count');

// Modals
const modalWazeLink = document.getElementById('modal-waze-link');
const btnCloseWazeModal = document.getElementById('btn-close-waze-modal');
const btnWazeModalDone = document.getElementById('btn-waze-modal-done');
const wazeDeeplinkInput = document.getElementById('waze-deeplink-input');
const btnCopyWazeLink = document.getElementById('btn-copy-waze-link');
const wazeQrCodeContainer = document.getElementById('waze-qr-code');

const modalNewPack = document.getElementById('modal-new-pack');
const btnCloseNewPackModal = document.getElementById('btn-close-new-pack-modal');
const btnCancelNewPack = document.getElementById('btn-cancel-new-pack');
const btnConfirmCreatePack = document.getElementById('btn-confirm-create-pack');
const newPackNameInput = document.getElementById('new-pack-name');
const newPackPresetSelect = document.getElementById('new-pack-preset');

const modalCloneVoice = document.getElementById('modal-clone-voice');
const btnOpenCloneModal = document.getElementById('btn-open-clone-modal');
const btnCloseCloneModal = document.getElementById('btn-close-clone-modal');
const btnCancelClone = document.getElementById('btn-cancel-clone');
const btnSubmitClone = document.getElementById('btn-submit-clone');
const cloneApiKeyInput = document.getElementById('clone-api-key');
const cloneVoiceNameInput = document.getElementById('clone-voice-name');
const cloneAudioFileInput = document.getElementById('clone-audio-file');
const fileDropArea = document.getElementById('file-drop-area');
const fileDropText = document.getElementById('file-drop-text');
const cloneStatusBox = document.getElementById('clone-status-box');

const modalCompanion = document.getElementById('modal-companion');
const btnOpenCompanion = document.getElementById('btn-open-companion');
const btnCloseCompanion = document.getElementById('btn-close-companion');
const btnCompanionDone = document.getElementById('btn-companion-done');
const companionCounter = document.getElementById('companion-counter');
const companionPromptTitle = document.getElementById('companion-prompt-title');
const companionPromptText = document.getElementById('companion-prompt-text');
const btnCompanionPrev = document.getElementById('btn-companion-prev');
const btnCompanionPlay = document.getElementById('btn-companion-play');
const btnCompanionNext = document.getElementById('btn-companion-next');

// --- Initialization ---

async function init() {
  setupEventListeners();
  await loadBaseMetadata();
  await loadPacksList();
}

async function loadBaseMetadata() {
  try {
    const res = await fetch(`${API_BASE}/api/prompts`);
    const data = await res.json();
    appState.promptsMeta = data.prompts;
    appState.presetsMeta = data.presets;
    appState.categories = data.categories;
    appState.validFilenames = data.valid_filenames;

    // Load Edge voices
    const vRes = await fetch(`${API_BASE}/api/voices/edge`);
    appState.edgeVoices = await vRes.json();
    populateEdgeVoices();
  } catch (err) {
    console.error('Fehler beim Laden der Basismetadaten:', err);
  }
}

function populateEdgeVoices() {
  selectEdgeVoice.innerHTML = '';
  appState.edgeVoices.forEach((v) => {
    const opt = document.createElement('option');
    opt.value = v.id;
    opt.textContent = v.name;
    if (v.recommended) opt.selected = true;
    selectEdgeVoice.appendChild(opt);
  });
}

async function loadPacksList() {
  try {
    const res = await fetch(`${API_BASE}/api/packs`);
    const data = await res.json();
    const packs = data.packs || [];

    selectActivePack.innerHTML = '';

    if (packs.length === 0) {
      // Auto-create a default starter pack
      await createInitialPack('German_Standard_Voice', 'standard');
      return;
    }

    packs.forEach((p) => {
      const opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = `${p.name} (${p.mp3_count}/43 - ${p.size_mb} MB)`;
      selectActivePack.appendChild(opt);
    });

    // Select the first pack by default or keep current
    if (!appState.activePackName || !packs.some((p) => p.name === appState.activePackName)) {
      appState.activePackName = packs[0].name;
    }
    selectActivePack.value = appState.activePackName;

    await loadActivePackDetails(appState.activePackName);
  } catch (err) {
    console.error('Fehler beim Laden der Packliste:', err);
  }
}

async function createInitialPack(name, presetId) {
  try {
    const res = await fetch(`${API_BASE}/api/packs/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        preset_id: presetId,
        engine: 'edge_tts',
        voice_id: 'de-DE-ConradNeural',
      }),
    });
    const data = await res.json();
    if (data.success) {
      appState.activePackName = data.pack.name;
      await loadPacksList();
    }
  } catch (err) {
    console.error('Initial pack creation error:', err);
  }
}

async function loadActivePackDetails(packName) {
  if (!packName) return;
  try {
    const res = await fetch(`${API_BASE}/api/packs/${packName}`);
    if (!res.ok) throw new Error('Pack Details konnten nicht geladen werden');
    const details = await res.json();
    appState.packDetails = details;

    updateHeaderStats();
    updateControlsFromMeta();
    renderPromptsList();
  } catch (err) {
    console.error('Fehler beim Laden der Pack-Details:', err);
  }
}

function updateHeaderStats() {
  const d = appState.packDetails;
  if (!d) return;

  statProgressVal.textContent = `${d.completed_count} / ${d.total_count}`;
  statSizeVal.textContent = `${d.size_mb.toFixed(2)} MB`;

  if (d.size_mb > 0.79) {
    statSizeVal.style.color = 'var(--accent-amber)';
    statStatusText.textContent = 'Zu groß (>0.8MB)';
    statStatusPill.className = 'stat-pill';
  } else if (d.completed_count === 43) {
    statSizeVal.style.color = 'var(--accent-green)';
    statStatusText.textContent = 'Waze-Bereit';
    statStatusPill.className = 'stat-pill status-ready';
  } else {
    statSizeVal.style.color = 'var(--text-main)';
    statStatusText.textContent = `${d.completed_count}/43 fertig`;
    statStatusPill.className = 'stat-pill';
  }
}

function updateControlsFromMeta() {
  const meta = appState.packDetails?.meta || {};
  if (meta.engine) {
    selectTtsEngine.value = meta.engine;
    toggleEngineUI(meta.engine);
  }
  if (meta.voice_id && meta.engine === 'edge_tts') {
    selectEdgeVoice.value = meta.voice_id;
  }
  if (meta.preset_id) {
    selectScriptPreset.value = meta.preset_id;
    updatePresetDescription(meta.preset_id);
  }
}

function toggleEngineUI(engine) {
  if (engine === 'elevenlabs') {
    engineBadge.textContent = 'ElevenLabs Voice-Clone';
    engineBadge.className = 'badge badge-accent';
    edgeVoiceGroup.classList.add('hidden');
    elevenlabsSettingsGroup.classList.remove('hidden');
  } else {
    engineBadge.textContent = 'Microsoft Neural (Kostenlos)';
    engineBadge.className = 'badge';
    edgeVoiceGroup.classList.remove('hidden');
    elevenlabsSettingsGroup.classList.add('hidden');
  }
}

function updatePresetDescription(presetId) {
  const preset = appState.presetsMeta[presetId];
  if (preset) {
    presetBadge.textContent = preset.name;
    presetDescriptionText.textContent = preset.description;
  }
}

// --- Prompt Cards Rendering ---

function renderPromptsList() {
  promptsContainer.innerHTML = '';
  const d = appState.packDetails;
  if (!d) return;

  const filenames = appState.validFilenames;
  const filtered = filenames.filter((fn) => {
    if (appState.activeCategory === 'all') return true;
    const meta = appState.promptsMeta[fn];
    return meta && meta.category === appState.activeCategory;
  });

  filtered.forEach((fn) => {
    const meta = appState.promptsMeta[fn] || {};
    const fileInfo = d.files[fn] || { exists: false, size_kb: 0, text: '' };

    const card = document.createElement('div');
    card.className = 'prompt-card';
    card.id = `card-${fn}`;

    const isGen = fileInfo.exists;
    const statusClass = isGen ? 'generated' : 'missing';
    const statusText = isGen ? `Bereit (${fileInfo.size_kb} KB)` : 'Noch offen';

    card.innerHTML = `
      <div class="prompt-card-header">
        <div class="prompt-info-left">
          <span class="prompt-title">${meta.title || fn}</span>
          <span class="prompt-filename">${fn} &bull; ${meta.description || ''}</span>
        </div>
        <span class="prompt-status-tag ${statusClass}" id="tag-${fn}">
          ${statusText}
        </span>
      </div>

      <textarea class="prompt-text-input" id="text-${fn}" data-filename="${fn}" placeholder="Ansagetext hier eingeben...">${fileInfo.text || ''}</textarea>

      <div class="prompt-card-actions">
        <div class="prompt-audio-actions">
          <button class="btn-play ${isGen ? '' : 'hidden'}" id="play-${fn}" data-filename="${fn}">
            <span class="play-icon">▶</span> Anhören
          </button>
        </div>
        <button class="prompt-gen-btn" id="gen-${fn}" data-filename="${fn}">
          ⚡ Neu generieren
        </button>
      </div>
    `;

    // Hook listeners
    const textarea = card.querySelector(`#text-${fn}`);
    textarea.addEventListener('change', () => onPromptTextChange(fn, textarea.value));

    const genBtn = card.querySelector(`#gen-${fn}`);
    genBtn.addEventListener('click', () => generateSingle(fn));

    const playBtn = card.querySelector(`#play-${fn}`);
    playBtn.addEventListener('click', () => togglePlayAudio(fn, playBtn));

    promptsContainer.appendChild(card);
  });
}

// --- Prompt Audio & Actions ---

async function onPromptTextChange(filename, text) {
  if (!appState.activePackName) return;
  try {
    await fetch(`${API_BASE}/api/packs/${appState.activePackName}/update_script`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, text }),
    });
    if (appState.packDetails && appState.packDetails.files[filename]) {
      appState.packDetails.files[filename].text = text;
    }
  } catch (err) {
    console.error('Error saving prompt text:', err);
  }
}

async function generateSingle(filename) {
  if (!appState.activePackName) return;
  const textarea = document.getElementById(`text-${filename}`);
  const text = textarea ? textarea.value : '';
  const genBtn = document.getElementById(`gen-${filename}`);

  const engine = selectTtsEngine.value;
  const voiceId = engine === 'elevenlabs' ? selectElevenlabsVoice.value : selectEdgeVoice.value;
  const apiKey = inputElevenlabsApiKey.value.trim();

  if (engine === 'elevenlabs' && (!apiKey || !voiceId)) {
    alert('Bitte gib zuerst deinen ElevenLabs API-Key ein und wähle eine Stimme aus!');
    return;
  }

  genBtn.disabled = true;
  genBtn.textContent = '⏳ Generiere...';

  try {
    const res = await fetch(`${API_BASE}/api/packs/${appState.activePackName}/generate_single`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename,
        text,
        engine,
        voice_id: voiceId,
        elevenlabs_api_key: apiKey,
      }),
    });

    if (!res.ok) throw new Error('Generierung fehlgeschlagen');
    const data = await res.json();

    // Update Card UI
    const tag = document.getElementById(`tag-${filename}`);
    if (tag) {
      tag.className = 'prompt-status-tag generated';
      tag.textContent = `Bereit (${data.size_kb} KB)`;
    }
    const playBtn = document.getElementById(`play-${filename}`);
    if (playBtn) playBtn.classList.remove('hidden');

    // Reload stats
    await loadActivePackDetails(appState.activePackName);
  } catch (err) {
    alert(`Fehler bei der Generierung von ${filename}: ${err.message}`);
  } finally {
    genBtn.disabled = false;
    genBtn.textContent = '⚡ Neu generieren';
  }
}

function togglePlayAudio(filename, btnElement) {
  const audioUrl = `${API_BASE}/api/audio/${appState.activePackName}/${filename}?t=${Date.now()}`;

  if (appState.currentAudio && appState.currentPlayingFilename === filename) {
    appState.currentAudio.pause();
    appState.currentAudio = null;
    appState.currentPlayingFilename = null;
    btnElement.classList.remove('playing');
    btnElement.innerHTML = '<span class="play-icon">▶</span> Anhören';
    return;
  }

  if (appState.currentAudio) {
    appState.currentAudio.pause();
    document.querySelectorAll('.btn-play').forEach((b) => {
      b.classList.remove('playing');
      b.innerHTML = '<span class="play-icon">▶</span> Anhören';
    });
  }

  const audio = new Audio(audioUrl);
  appState.currentAudio = audio;
  appState.currentPlayingFilename = filename;

  btnElement.classList.add('playing');
  btnElement.innerHTML = '<span class="play-icon">⏸</span> Stopp';

  audio.onended = () => {
    btnElement.classList.remove('playing');
    btnElement.innerHTML = '<span class="play-icon">▶</span> Anhören';
    appState.currentAudio = null;
    appState.currentPlayingFilename = null;
  };

  audio.onerror = () => {
    btnElement.classList.remove('playing');
    btnElement.innerHTML = '<span class="play-icon">▶</span> Anhören';
    appState.currentAudio = null;
    appState.currentPlayingFilename = null;
    alert('Audiodatei konnte nicht abgespielt werden.');
  };

  audio.play();
}

// --- Batch Generation ---

async function generateAllPrompts() {
  if (!appState.activePackName) return;
  const engine = selectTtsEngine.value;
  const voiceId = engine === 'elevenlabs' ? selectElevenlabsVoice.value : selectEdgeVoice.value;
  const apiKey = inputElevenlabsApiKey.value.trim();

  if (engine === 'elevenlabs' && (!apiKey || !voiceId)) {
    alert('Bitte gib zuerst deinen ElevenLabs API-Key ein und wähle eine Stimme aus!');
    return;
  }

  const confirmed = confirm(
    `Möchtest du alle 43 Ansagen für "${appState.activePackName}" automatisch generieren?\nEngine: ${engine === 'elevenlabs' ? 'ElevenLabs' : 'Microsoft Neural'}`
  );
  if (!confirmed) return;

  btnGenerateAll.disabled = true;
  btnGenerateAll.innerHTML = '<span class="icon">⏳</span> Generiere 43 Ansagen...';
  batchProgressContainer.classList.remove('hidden');
  batchProgressFill.style.width = '35%';
  batchProgressCount.textContent = 'Verarbeite...';

  try {
    const res = await fetch(`${API_BASE}/api/packs/${appState.activePackName}/generate_all`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        engine,
        voice_id: voiceId,
        elevenlabs_api_key: apiKey,
      }),
    });

    if (!res.ok) throw new Error('Batch-Generierung fehlgeschlagen');
    const data = await res.json();

    batchProgressFill.style.width = '100%';
    batchProgressCount.textContent = `${data.generated_count} / ${data.total} fertig`;

    setTimeout(() => {
      batchProgressContainer.classList.add('hidden');
    }, 2500);

    await loadActivePackDetails(appState.activePackName);
    alert(`Erfolgreich! ${data.generated_count} von ${data.total} Ansagen wurden generiert.\nPack-Größe: ${data.size_mb} MB (Waze-kompatibel).`);
  } catch (err) {
    alert(`Fehler bei der Batch-Generierung: ${err.message}`);
  } finally {
    btnGenerateAll.disabled = false;
    btnGenerateAll.innerHTML = '<span class="icon">⚡</span> Alle 43 Ansagen generieren';
  }
}

// --- Waze Upload & Deep Link Modal ---

async function uploadToWazeCloud() {
  if (!appState.activePackName) return;

  btnUploadWaze.disabled = true;
  btnUploadWaze.innerHTML = '<span class="icon">⏳</span> Lade zu Waze hoch...';

  try {
    const res = await fetch(`${API_BASE}/api/packs/${appState.activePackName}/upload_to_waze`, {
      method: 'POST',
    });
    const data = await res.json();

    if (!data.success) {
      throw new Error(data.error || 'Waze Cloud Upload fehlgeschlagen');
    }

    // Show Modal with Link and QR Code
    wazeDeeplinkInput.value = data.deep_link;

    // Render QR Code
    wazeQrCodeContainer.innerHTML = '';
    new QRCode(wazeQrCodeContainer, {
      text: data.deep_link,
      width: 180,
      height: 180,
      colorDark: '#041226',
      colorLight: '#ffffff',
      correctLevel: QRCode.CorrectLevel.M,
    });

    modalWazeLink.classList.remove('hidden');
  } catch (err) {
    alert(`Waze Upload Fehler: ${err.message}`);
  } finally {
    btnUploadWaze.disabled = false;
    btnUploadWaze.innerHTML = '<span class="icon">🚀</span> 1-Klick Waze Link';
  }
}

// --- Live Companion Recorder ---

function openCompanionMode() {
  if (!appState.packDetails) return;
  appState.companionIndex = 0;
  updateCompanionCard();
  modalCompanion.classList.remove('hidden');
}

function updateCompanionCard() {
  const filenames = appState.validFilenames;
  const currentFn = filenames[appState.companionIndex];
  const meta = appState.promptsMeta[currentFn] || {};
  const fileInfo = appState.packDetails?.files[currentFn] || {};

  companionCounter.textContent = `Ansage ${appState.companionIndex + 1} von ${filenames.length} (${currentFn})`;
  companionPromptTitle.textContent = meta.title || currentFn;
  companionPromptText.textContent = `"${fileInfo.text || meta.standard || ''}"`;

  btnCompanionPrev.disabled = appState.companionIndex === 0;
  btnCompanionNext.disabled = appState.companionIndex === filenames.length - 1;
}

function companionPlayCurrent() {
  const filenames = appState.validFilenames;
  const currentFn = filenames[appState.companionIndex];
  togglePlayAudio(currentFn, btnCompanionPlay);
}

// --- Event Listeners Setup ---

function setupEventListeners() {
  // Pack selector
  selectActivePack.addEventListener('change', (e) => {
    appState.activePackName = e.target.value;
    loadActivePackDetails(appState.activePackName);
  });

  btnRefreshPacks.addEventListener('click', loadPacksList);

  // Engine switch
  selectTtsEngine.addEventListener('change', (e) => {
    toggleEngineUI(e.target.value);
  });

  // Preset switch
  selectScriptPreset.addEventListener('change', (e) => {
    updatePresetDescription(e.target.value);
  });

  // Apply Preset to all 43 prompts
  btnApplyPreset.addEventListener('click', async () => {
    if (!appState.activePackName) return;
    const presetId = selectScriptPreset.value;
    const confirmed = confirm(`Möchtest du das Preset "${presetId}" auf alle 43 Texte in "${appState.activePackName}" übertragen?`);
    if (!confirmed) return;

    try {
      const res = await fetch(`${API_BASE}/api/packs/${appState.activePackName}/apply_preset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset_id: presetId }),
      });
      if (res.ok) {
        await loadActivePackDetails(appState.activePackName);
        alert('Preset-Texte erfolgreich übernommen!');
      }
    } catch (err) {
      console.error(err);
    }
  });

  // Category filter tabs
  categoryTabs.addEventListener('click', (e) => {
    if (e.target.classList.contains('tab-btn')) {
      document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
      e.target.classList.add('active');
      appState.activeCategory = e.target.dataset.category;
      renderPromptsList();
    }
  });

  // Master Pack Actions
  btnGenerateAll.addEventListener('click', generateAllPrompts);
  btnUploadWaze.addEventListener('click', uploadToWazeCloud);

  btnOptimizeSize.addEventListener('click', async () => {
    if (!appState.activePackName) return;
    btnOptimizeSize.disabled = true;
    btnOptimizeSize.textContent = '🎛️ Optimiere...';
    try {
      const res = await fetch(`${API_BASE}/api/packs/${appState.activePackName}/optimize`, { method: 'POST' });
      const data = await res.json();
      await loadActivePackDetails(appState.activePackName);
      alert(`Pack optimiert! Neue Größe: ${data.final_size_mb} MB (${data.bitrate_kbps} kbps Mono).`);
    } catch (err) {
      alert('Optimierungsfehler');
    } finally {
      btnOptimizeSize.disabled = false;
      btnOptimizeSize.innerHTML = '<span class="icon">🎛️</span> Größe optimieren';
    }
  });

  btnDownloadZip.addEventListener('click', () => {
    if (!appState.activePackName) return;
    window.location.href = `${API_BASE}/api/packs/${appState.activePackName}/download_zip`;
  });

  // ElevenLabs fetch voices
  btnLoadElevenlabsVoices.addEventListener('click', async () => {
    const key = inputElevenlabsApiKey.value.trim();
    if (!key) {
      alert('Bitte ElevenLabs API-Key eingeben');
      return;
    }
    btnLoadElevenlabsVoices.disabled = true;
    btnLoadElevenlabsVoices.textContent = 'Lade...';
    try {
      const res = await fetch(`${API_BASE}/api/elevenlabs/voices`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key }),
      });
      const data = await res.json();
      selectElevenlabsVoice.innerHTML = '';
      if (data.voices && data.voices.length > 0) {
        data.voices.forEach((v) => {
          const opt = document.createElement('option');
          opt.value = v.id;
          opt.textContent = v.name;
          selectElevenlabsVoice.appendChild(opt);
        });
        alert(`${data.voices.length} Stimmen von ElevenLabs geladen!`);
      } else {
        alert('Keine Stimmen gefunden oder ungültiger API-Key.');
      }
    } catch (err) {
      alert('Fehler beim Abrufen der ElevenLabs Stimmen');
    } finally {
      btnLoadElevenlabsVoices.disabled = false;
      btnLoadElevenlabsVoices.textContent = 'Stimmen laden';
    }
  });

  // Modals handling
  btnNewPack.addEventListener('click', () => modalNewPack.classList.remove('hidden'));
  btnCloseNewPackModal.addEventListener('click', () => modalNewPack.classList.add('hidden'));
  btnCancelNewPack.addEventListener('click', () => modalNewPack.classList.add('hidden'));

  btnConfirmCreatePack.addEventListener('click', async () => {
    const name = newPackNameInput.value.trim();
    const preset = newPackPresetSelect.value;
    if (!name) {
      alert('Bitte einen Namen eingeben');
      return;
    }
    await createInitialPack(name, preset);
    modalNewPack.classList.add('hidden');
    newPackNameInput.value = '';
  });

  // Waze modal
  btnCloseWazeModal.addEventListener('click', () => modalWazeLink.classList.add('hidden'));
  btnWazeModalDone.addEventListener('click', () => modalWazeLink.classList.add('hidden'));
  btnCopyWazeLink.addEventListener('click', () => {
    wazeDeeplinkInput.select();
    navigator.clipboard.writeText(wazeDeeplinkInput.value);
    btnCopyWazeLink.textContent = 'Kopiert!';
    setTimeout(() => {
      btnCopyWazeLink.textContent = 'Kopieren';
    }, 2000);
  });

  // Voice Clone Modal
  btnOpenCloneModal.addEventListener('click', () => modalCloneVoice.classList.remove('hidden'));
  btnCloseCloneModal.addEventListener('click', () => modalCloneVoice.classList.add('hidden'));
  btnCancelClone.addEventListener('click', () => modalCloneVoice.classList.add('hidden'));

  fileDropArea.addEventListener('click', () => cloneAudioFileInput.click());
  cloneAudioFileInput.addEventListener('change', () => {
    if (cloneAudioFileInput.files.length > 0) {
      fileDropText.textContent = `Ausgewählt: ${cloneAudioFileInput.files[0].name}`;
    }
  });

  btnSubmitClone.addEventListener('click', async () => {
    const apiKey = cloneApiKeyInput.value.trim();
    const name = cloneVoiceNameInput.value.trim();
    const file = cloneAudioFileInput.files[0];

    if (!apiKey || !name || !file) {
      alert('Bitte API-Key, Stimmen-Name und eine Audio-Datei angeben!');
      return;
    }

    const formData = new FormData();
    formData.append('api_key', apiKey);
    formData.append('name', name);
    formData.append('description', `YouTuber Clone ${name} für Waze`);
    formData.append('audio_file', file);

    btnSubmitClone.disabled = true;
    btnSubmitClone.textContent = '⏳ Trainiere & Klone Stimme...';
    cloneStatusBox.classList.remove('hidden');
    cloneStatusBox.textContent = 'Lade Audiodatei hoch und trainiere KI-Modell bei ElevenLabs...';

    try {
      const res = await fetch(`${API_BASE}/api/elevenlabs/clone`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.detail || 'Klonen fehlgeschlagen');
      }

      cloneStatusBox.textContent = `Erfolg! Stimme "${name}" wurde geklont (ID: ${data.voice_id}).`;
      inputElevenlabsApiKey.value = apiKey;
      selectTtsEngine.value = 'elevenlabs';
      toggleEngineUI('elevenlabs');

      // Add to select
      const opt = document.createElement('option');
      opt.value = data.voice_id;
      opt.textContent = `${name} (Neu geklont)`;
      opt.selected = true;
      selectElevenlabsVoice.appendChild(opt);

      setTimeout(() => {
        modalCloneVoice.classList.add('hidden');
        btnSubmitClone.disabled = false;
        btnSubmitClone.textContent = 'Stimme trainieren & klonen';
      }, 2000);
    } catch (err) {
      cloneStatusBox.textContent = `Fehler: ${err.message}`;
      btnSubmitClone.disabled = false;
      btnSubmitClone.textContent = 'Stimme trainieren & klonen';
    }
  });

  // Companion modal
  btnOpenCompanion.addEventListener('click', openCompanionMode);
  btnCloseCompanion.addEventListener('click', () => modalCompanion.classList.add('hidden'));
  btnCompanionDone.addEventListener('click', () => modalCompanion.classList.add('hidden'));

  btnCompanionPrev.addEventListener('click', () => {
    if (appState.companionIndex > 0) {
      appState.companionIndex--;
      updateCompanionCard();
    }
  });

  btnCompanionNext.addEventListener('click', () => {
    if (appState.companionIndex < appState.validFilenames.length - 1) {
      appState.companionIndex++;
      updateCompanionCard();
    }
  });

  btnCompanionPlay.addEventListener('click', companionPlayCurrent);
}

// Run init on DOM ready
document.addEventListener('DOMContentLoaded', init);
