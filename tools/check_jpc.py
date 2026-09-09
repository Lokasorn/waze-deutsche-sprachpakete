import urllib.request
import json
import re

# Search JPC API or Buecher.de or Thalia for Paw Patrol Hörspiel
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Let's test JPC search
url = "https://www.jpc.de/s/paw+patrol+h%C3%B6rspiel"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print("JPC len:", len(html))
        # look for audio samples (.mp3)
        mp3s = re.findall(r'https?://[^\s\'"]+\.mp3[^\s\'"]*', html)
        print("Found MP3s on JPC:", mp3s[:10])
        # Also look for data-sound or audio preview links
        previews = re.findall(r'data-[a-z-]*audio[^\'"=]*=[\'"]([^\'"]+)[\'"]', html, re.I)
        print("Audio data attrs:", previews[:10])
        # Also look for sample URLs
        samples = re.findall(r'https?://[^\s\'"]*sample[^\s\'"]*', html)
        print("Sample URLs:", samples[:10])
except Exception as e:
    print("JPC Err:", e)
