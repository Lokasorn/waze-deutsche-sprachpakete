import urllib.request
import re

req = urllib.request.Request(
    'https://www.toggo.de/paw-patrol',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
)
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print('Len:', len(html))
        m = re.findall(r'href=[\'"]([^\'"]*videos[^\'"]*)[\'"]', html)
        print('Video links:', m[:10])
        # Also check for JSON or API data
        apis = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', html)
        print('m3u8:', apis)
except Exception as e:
    print('Err:', e)
