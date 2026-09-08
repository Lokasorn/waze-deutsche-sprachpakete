"""
Upload MontanaBlack Voicepack directly to Waze Cloud API
to generate the official 1-click install link (https://waze.com/ul?acvp=...)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from backend.waze_uploader import upload_soundpack_to_waze

pack_name = "MontanaBlack_DE"
pack_folder = str(BASE_DIR / "packs" / "MontanaBlack")

print(f"🚀 Starte Waze Cloud Upload für Pack: {pack_name}...")
result = upload_soundpack_to_waze(pack_name, pack_folder)

if result.get("success"):
    print("\n" + "=" * 60)
    print("🎉 UPLOAD ERFOLGREICH!")
    print("=" * 60)
    print(f"📱 1-Klick Waze Link:  {result['deep_link']}")
    print(f"📦 Direkter Download: {result['download_link']}")
    print(f"🆔 Pack UUID:         {result['pack_uuid']}")
    print(f"📊 Dateigröße:        {result['size_mb']} MB")
    print("=" * 60)
else:
    print("\n❌ Upload fehlgeschlagen:")
    print(result.get("error"))
