"""
FastAPI Server for Waze German Voice Studio.
Serves REST APIs for prompt management, TTS generation, audio optimization,
and Waze deep-link publishing, alongside a sleek modern web UI.
"""

import asyncio
import io
import json
import os
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.audio_processor import (
    compress_pack_to_limit,
    convert_and_optimize_file,
    get_folder_size_mb,
)
from backend.voice_engine import (
    EDGE_GERMAN_VOICES,
    clone_voice_elevenlabs,
    generate_edge_tts,
    generate_elevenlabs_tts,
    get_elevenlabs_voices,
)
from backend.waze_prompts import (
    CATEGORIES,
    PRESETS,
    PROMPT_METADATA,
    VALID_WAZE_FILENAMES,
)
from backend.waze_uploader import upload_soundpack_to_waze

BASE_DIR = Path(__file__).resolve().parent.parent
PACKS_DIR = BASE_DIR / "packs"
FRONTEND_DIR = BASE_DIR / "frontend"

os.makedirs(PACKS_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

app = FastAPI(title="Waze Voice Studio", description="Create custom German Waze voicepacks with AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request Models ---
class CreatePackRequest(BaseModel):
    name: str
    preset_id: str = "standard"
    engine: str = "edge_tts"
    voice_id: str = "de-DE-ConradNeural"
    elevenlabs_api_key: Optional[str] = None


class UpdateScriptRequest(BaseModel):
    filename: str
    text: str


class GenerateSingleRequest(BaseModel):
    filename: str
    text: str
    engine: str = "edge_tts"
    voice_id: str = "de-DE-ConradNeural"
    elevenlabs_api_key: Optional[str] = None


class GenerateAllRequest(BaseModel):
    engine: str = "edge_tts"
    voice_id: str = "de-DE-ConradNeural"
    elevenlabs_api_key: Optional[str] = None


# --- Helper Functions ---
def get_pack_meta_path(pack_name: str) -> Path:
    return PACKS_DIR / pack_name / "pack_meta.json"


def load_pack_meta(pack_name: str) -> Dict[str, Any]:
    meta_path = get_pack_meta_path(pack_name)
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_pack_meta(pack_name: str, meta: Dict[str, Any]):
    meta_path = get_pack_meta_path(pack_name)
    os.makedirs(meta_path.parent, exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


# --- API Endpoints ---

@app.get("/api/prompts")
def get_prompts():
    """Return all 43 prompt definitions, categories, and presets."""
    return {
        "categories": CATEGORIES,
        "presets": PRESETS,
        "prompts": PROMPT_METADATA,
        "valid_filenames": VALID_WAZE_FILENAMES,
    }


@app.get("/api/voices/edge")
def get_edge_voices():
    """Return list of free Microsoft Edge neural German voices."""
    return EDGE_GERMAN_VOICES


@app.post("/api/elevenlabs/voices")
def get_user_elevenlabs_voices(data: Dict[str, str]):
    """Fetch user's voices from ElevenLabs using their API key."""
    api_key = data.get("api_key", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API-Key erforderlich")
    voices = get_elevenlabs_voices(api_key)
    return {"voices": voices}


@app.post("/api/elevenlabs/clone")
async def clone_elevenlabs_voice(
    api_key: str = Form(...),
    name: str = Form(...),
    description: str = Form("Waze Voicepack"),
    audio_file: UploadFile = File(...),
):
    """Clones a voice on ElevenLabs using an uploaded audio file."""
    temp_dir = BASE_DIR / "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = temp_dir / audio_file.filename

    with open(temp_file, "wb") as f:
        shutil.copyfileobj(audio_file.file, f)

    voice_id = clone_voice_elevenlabs(api_key, name, str(temp_file), description)

    if temp_file.exists():
        os.remove(temp_file)

    if not voice_id:
        raise HTTPException(status_code=500, detail="Fehler beim Klonen der Stimme bei ElevenLabs")

    return {"success": True, "voice_id": voice_id, "name": name}


@app.get("/api/packs")
def list_packs():
    """List all created voice packs."""
    packs = []
    if PACKS_DIR.exists():
        for d in PACKS_DIR.iterdir():
            if d.is_dir():
                meta = load_pack_meta(d.name)
                size_mb = round(get_folder_size_mb(str(d)), 3)
                mp3_count = len([f for f in d.iterdir() if f.name.endswith(".mp3") and f.name in VALID_WAZE_FILENAMES])
                packs.append({
                    "name": d.name,
                    "preset_id": meta.get("preset_id", "standard"),
                    "engine": meta.get("engine", "edge_tts"),
                    "voice_id": meta.get("voice_id", "de-DE-ConradNeural"),
                    "size_mb": size_mb,
                    "mp3_count": mp3_count,
                    "is_complete": mp3_count == len(VALID_WAZE_FILENAMES),
                    "deep_link": meta.get("deep_link", None),
                })
    return {"packs": packs}


@app.post("/api/packs/create")
def create_pack(req: CreatePackRequest):
    """Create a new soundpack with the specified preset."""
    pack_name = req.name.strip().replace(" ", "_")
    if not pack_name:
        raise HTTPException(status_code=400, detail="Ungültiger Pack-Name")

    pack_dir = PACKS_DIR / pack_name
    os.makedirs(pack_dir, exist_ok=True)

    preset_id = req.preset_id if req.preset_id in PRESETS else "standard"

    # Initialize scripts from preset
    scripts = {}
    for filename, data in PROMPT_METADATA.items():
        scripts[filename] = data.get(preset_id, data.get("standard", ""))

    meta = {
        "name": pack_name,
        "preset_id": preset_id,
        "engine": req.engine,
        "voice_id": req.voice_id,
        "scripts": scripts,
        "deep_link": None,
    }
    save_pack_meta(pack_name, meta)
    return {"success": True, "pack": meta}


@app.get("/api/packs/{pack_name}")
def get_pack_details(pack_name: str):
    """Get all details, scripts, and audio file status for a pack."""
    pack_dir = PACKS_DIR / pack_name
    if not pack_dir.exists():
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    meta = load_pack_meta(pack_name)
    scripts = meta.get("scripts", {})

    files_status = {}
    for filename in VALID_WAZE_FILENAMES:
        file_path = pack_dir / filename
        exists = file_path.exists()
        size_kb = round(file_path.stat().st_size / 1024, 1) if exists else 0
        files_status[filename] = {
            "exists": exists,
            "size_kb": size_kb,
            "text": scripts.get(filename, PROMPT_METADATA[filename].get("standard", "")),
        }

    size_mb = round(get_folder_size_mb(str(pack_dir)), 3)
    completed = sum(1 for f in files_status.values() if f["exists"])

    return {
        "name": pack_name,
        "meta": meta,
        "size_mb": size_mb,
        "completed_count": completed,
        "total_count": len(VALID_WAZE_FILENAMES),
        "is_ready_for_waze": size_mb <= 0.79 and completed > 0,
        "files": files_status,
    }


@app.post("/api/packs/{pack_name}/update_script")
def update_pack_script(pack_name: str, req: UpdateScriptRequest):
    """Updates text script for a single prompt."""
    meta = load_pack_meta(pack_name)
    if not meta:
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    meta.setdefault("scripts", {})[req.filename] = req.text
    save_pack_meta(pack_name, meta)
    return {"success": True}


@app.post("/api/packs/{pack_name}/apply_preset")
def apply_preset_to_pack(pack_name: str, data: Dict[str, str]):
    """Applies a preset to all prompts in the pack."""
    preset_id = data.get("preset_id", "standard")
    meta = load_pack_meta(pack_name)
    if not meta:
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    scripts = {}
    for filename, pdata in PROMPT_METADATA.items():
        scripts[filename] = pdata.get(preset_id, pdata.get("standard", ""))

    meta["preset_id"] = preset_id
    meta["scripts"] = scripts
    save_pack_meta(pack_name, meta)
    return {"success": True, "scripts": scripts}


@app.post("/api/packs/{pack_name}/generate_single")
async def generate_single_prompt(pack_name: str, req: GenerateSingleRequest):
    """Generates audio for a single prompt and optimizes it."""
    pack_dir = PACKS_DIR / pack_name
    if not pack_dir.exists():
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    target_file = pack_dir / req.filename
    temp_raw = pack_dir / f"temp_{req.filename}"

    # Generate raw audio
    if req.engine == "elevenlabs" and req.elevenlabs_api_key:
        ok = generate_elevenlabs_tts(req.elevenlabs_api_key, req.voice_id, req.text, str(temp_raw))
        if not ok:
            raise HTTPException(status_code=500, detail="Fehler bei ElevenLabs Sprachgenerierung")
    else:
        # Default: Edge-TTS
        await generate_edge_tts(req.text, voice_id=req.voice_id, output_path=str(temp_raw))

    # Convert, normalize (+7dB boost) and mono-encode
    convert_and_optimize_file(str(temp_raw), str(target_file), bitrate_kbps=32)

    if temp_raw.exists():
        os.remove(temp_raw)

    # Save script text
    meta = load_pack_meta(pack_name)
    meta.setdefault("scripts", {})[req.filename] = req.text
    save_pack_meta(pack_name, meta)

    return {
        "success": True,
        "filename": req.filename,
        "size_kb": round(target_file.stat().st_size / 1024, 1),
    }


@app.post("/api/packs/{pack_name}/generate_all")
async def generate_all_prompts(pack_name: str, req: GenerateAllRequest):
    """Generates audio for all 43 prompts in batch."""
    pack_dir = PACKS_DIR / pack_name
    if not pack_dir.exists():
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    meta = load_pack_meta(pack_name)
    scripts = meta.get("scripts", {})

    success_count = 0
    errors = []

    for filename in VALID_WAZE_FILENAMES:
        text = scripts.get(filename, PROMPT_METADATA[filename].get("standard", ""))
        target_file = pack_dir / filename
        temp_raw = pack_dir / f"temp_{filename}"

        try:
            if req.engine == "elevenlabs" and req.elevenlabs_api_key:
                ok = generate_elevenlabs_tts(req.elevenlabs_api_key, req.voice_id, text, str(temp_raw))
                if not ok:
                    errors.append(f"Fehler bei {filename}")
                    continue
            else:
                await generate_edge_tts(text, voice_id=req.voice_id, output_path=str(temp_raw))

            convert_and_optimize_file(str(temp_raw), str(target_file), bitrate_kbps=32)
            if temp_raw.exists():
                os.remove(temp_raw)
            success_count += 1
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")

    # Compress whole pack to be strictly under 0.78 MB
    compress_pack_to_limit(str(pack_dir), target_max_mb=0.78)

    meta["engine"] = req.engine
    meta["voice_id"] = req.voice_id
    save_pack_meta(pack_name, meta)

    return {
        "success": True,
        "generated_count": success_count,
        "total": len(VALID_WAZE_FILENAMES),
        "size_mb": round(get_folder_size_mb(str(pack_dir)), 3),
        "errors": errors,
    }


@app.post("/api/packs/{pack_name}/upload_audio")
async def upload_custom_audio(
    pack_name: str,
    filename: str = Form(...),
    audio_file: UploadFile = File(...),
):
    """Uploads a manual custom audio file (MP3/WAV) for a specific prompt."""
    pack_dir = PACKS_DIR / pack_name
    if not pack_dir.exists():
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    if filename not in VALID_WAZE_FILENAMES:
        raise HTTPException(status_code=400, detail="Ungültiger Waze-Dateiname")

    temp_raw = pack_dir / f"upload_temp_{filename}"
    target_file = pack_dir / filename

    with open(temp_raw, "wb") as f:
        shutil.copyfileobj(audio_file.file, f)

    # Convert to standard Waze Mono MP3
    convert_and_optimize_file(str(temp_raw), str(target_file), bitrate_kbps=32)

    if temp_raw.exists():
        os.remove(temp_raw)

    return {
        "success": True,
        "filename": filename,
        "size_kb": round(target_file.stat().st_size / 1024, 1),
    }


@app.get("/api/audio/{pack_name}/{filename}")
def stream_audio(pack_name: str, filename: str):
    """Streams the MP3 file for in-browser playback."""
    file_path = PACKS_DIR / pack_name / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audiodatei nicht gefunden")
    return FileResponse(path=file_path, media_type="audio/mpeg", filename=filename)


@app.post("/api/packs/{pack_name}/optimize")
def optimize_pack(pack_name: str):
    """Enforces strict Waze compression limit (<= 0.78 MB)."""
    pack_dir = PACKS_DIR / pack_name
    if not pack_dir.exists():
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    success, final_size, br = compress_pack_to_limit(str(pack_dir), target_max_mb=0.78)
    return {
        "success": success,
        "final_size_mb": round(final_size, 3),
        "bitrate_kbps": br,
    }


@app.post("/api/packs/{pack_name}/upload_to_waze")
def upload_to_waze(pack_name: str):
    """Uploads the pack to Waze cloud servers and generates the acvp deep-link."""
    pack_dir = PACKS_DIR / pack_name
    if not pack_dir.exists():
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    result = upload_soundpack_to_waze(pack_name, str(pack_dir))
    if result.get("success"):
        meta = load_pack_meta(pack_name)
        meta["deep_link"] = result["deep_link"]
        meta["pack_uuid"] = result["pack_uuid"]
        save_pack_meta(pack_name, meta)

    return result


@app.get("/api/packs/{pack_name}/download_zip")
def download_pack_zip(pack_name: str):
    """Creates and returns a ZIP archive containing all 43 Waze MP3 files."""
    pack_dir = PACKS_DIR / pack_name
    if not pack_dir.exists():
        raise HTTPException(status_code=404, detail="Pack nicht gefunden")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for f in pack_dir.iterdir():
            if f.name.endswith(".mp3") and f.name in VALID_WAZE_FILENAMES:
                zip_file.write(f, arcname=f.name)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={pack_name}_waze_voicepack.zip"},
    )


# Serve frontend static assets
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
