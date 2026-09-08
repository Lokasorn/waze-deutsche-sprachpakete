"""
Voice Engine supporting Edge-TTS (Free neural German voices)
and ElevenLabs (Instant YouTuber voice cloning & high-end TTS).
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import edge_tts
import requests

EDGE_GERMAN_VOICES = [
    {
        "id": "de-DE-ConradNeural",
        "name": "Conrad (Männlich, Seriös & Dynamisch)",
        "gender": "male",
        "locale": "de-DE",
        "recommended": True,
    },
    {
        "id": "de-DE-KillianNeural",
        "name": "Killian (Männlich, Natürlich & Warm)",
        "gender": "male",
        "locale": "de-DE",
        "recommended": False,
    },
    {
        "id": "de-DE-FlorianMultilingualNeural",
        "name": "Florian (Männlich, Modern & Locker)",
        "gender": "male",
        "locale": "de-DE",
        "recommended": True,
    },
    {
        "id": "de-DE-KatjaNeural",
        "name": "Katja (Weiblich, Lebendig & Klar)",
        "gender": "female",
        "locale": "de-DE",
        "recommended": True,
    },
    {
        "id": "de-DE-AmalaNeural",
        "name": "Amala (Weiblich, Freundlich)",
        "gender": "female",
        "locale": "de-DE",
        "recommended": False,
    },
    {
        "id": "de-DE-SeraphinaMultilingualNeural",
        "name": "Seraphina (Weiblich, Modern)",
        "gender": "female",
        "locale": "de-DE",
        "recommended": False,
    },
    {
        "id": "de-AT-IngridNeural",
        "name": "Ingrid (Österreichisch, Charmant)",
        "gender": "female",
        "locale": "de-AT",
        "recommended": False,
    },
    {
        "id": "de-CH-JanNeural",
        "name": "Jan (Schweizerdeutsch, Sympathisch)",
        "gender": "male",
        "locale": "de-CH",
        "recommended": False,
    },
]


async def generate_edge_tts(
    text: str,
    voice_id: str = "de-DE-ConradNeural",
    output_path: str = "",
    rate: str = "+0%",
    pitch: str = "+0Hz",
) -> str:
    """Generates an MP3 file using Microsoft Edge Neural TTS."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    communicate = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
    await communicate.save(output_path)
    return output_path


def get_elevenlabs_voices(api_key: str) -> List[Dict[str, Any]]:
    """Fetch available voices (including custom cloned voices) from ElevenLabs."""
    if not api_key:
        return []
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            voices = []
            for v in data.get("voices", []):
                category = v.get("category", "")
                voices.append({
                    "id": v["voice_id"],
                    "name": f"{v['name']} ({'Geklont' if category == 'cloned' else category})",
                    "category": category,
                    "preview_url": v.get("preview_url", ""),
                })
            return voices
        else:
            print(f"ElevenLabs error fetching voices: {response.text}")
            return []
    except Exception as e:
        print(f"ElevenLabs request exception: {e}")
        return []


def clone_voice_elevenlabs(api_key: str, name: str, audio_file_path: str, description: str = "Waze Custom Voice") -> Optional[str]:
    """
    Clones a new voice in ElevenLabs using an uploaded audio file (1-5 minutes of speech).
    Returns the newly created voice_id.
    """
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {"xi-api-key": api_key}
    try:
        with open(audio_file_path, "rb") as f:
            files = [("files", (os.path.basename(audio_file_path), f, "audio/mpeg"))]
            data = {
                "name": name,
                "description": description,
            }
            response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
            if response.status_code in (200, 201):
                voice_id = response.json().get("voice_id")
                return voice_id
            else:
                print(f"ElevenLabs clone error: {response.text}")
                return None
    except Exception as e:
        print(f"ElevenLabs clone exception: {e}")
        return None


def generate_elevenlabs_tts(
    api_key: str,
    voice_id: str,
    text: str,
    output_path: str,
    model_id: str = "eleven_multilingual_v2",
) -> bool:
    """Generates audio using ElevenLabs cloned or default voice."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"ElevenLabs TTS error: {response.text}")
            return False
    except Exception as e:
        print(f"ElevenLabs TTS exception: {e}")
        return False
