"""
Launcher script for Waze German Voice Studio.
Starts the FastAPI backend and automatically opens the user's web browser.
"""

import os
import sys
import webbrowser
from pathlib import Path

# Ensure backend can be imported
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure WinGet / local FFmpeg path is included in environment
local_app_data = os.environ.get("LOCALAPPDATA", "")
winget_links = os.path.join(local_app_data, "Microsoft", "WinGet", "Links")
if os.path.exists(winget_links) and winget_links not in os.environ.get("PATH", ""):
    os.environ["PATH"] = winget_links + os.pathsep + os.environ.get("PATH", "")

import uvicorn


def main():
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print("=" * 65)
    print("   🎙️  WAZE GERMAN VOICE STUDIO  🎙️")
    print("=" * 65)
    print(f"🚀 Starte Server unter: {url}")
    print("📱 Erstelle, klone und exportiere deutsche Soundpacks für Waze.")
    print("   Drücke Strg+C zum Beenden.")
    print("=" * 65 + "\n")

    # Open browser automatically after a short moment
    def open_browser():
        import time
        time.sleep(1.2)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("backend.app:app", host=host, port=port, reload=False, log_level="info")


if __name__ == "__main__":
    main()
