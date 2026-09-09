import base64
import json
import os
import sys
import tarfile
import time
import uuid
from pathlib import Path
import subprocess
import blackboxprotobuf
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ffmpeg_shared_bin = r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build-shared\bin"
if os.path.exists(ffmpeg_shared_bin) and ffmpeg_shared_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_shared_bin + os.pathsep + os.environ.get("PATH", "")

WORKSPACE_DIR = Path(r"c:\Users\PC\Desktop\Waze German Voice")
OUTPUT_PACK_DIR = WORKSPACE_DIR / "packs" / "PawPatrolRubble"
OUTPUT_PACK_DIR.mkdir(parents=True, exist_ok=True)
TEMP_RAW_DIR = WORKSPACE_DIR / "tools" / "rubble_raw_43"
TEMP_RAW_DIR.mkdir(parents=True, exist_ok=True)

FISH_API_KEY = "sk-fish-ngV4tP1Ft-2VAwa6xeG3grjEvoA0bGn6PULhtY1S2rM"
FISH_MODEL_ID = "0914c177af5a4b59aadb3e670acd56d1"
FISH_API_URL = "https://api.fish.audio/v1/tts"

VALID_WAZE_FILENAMES = [
    "StartDrive1.mp3", "StartDrive2.mp3", "StartDrive3.mp3", "StartDrive4.mp3",
    "StartDrive5.mp3", "StartDrive6.mp3", "StartDrive7.mp3", "StartDrive8.mp3",
    "StartDrive9.mp3", "200.mp3", "200meters.mp3", "400.mp3", "400meters.mp3",
    "800.mp3", "800meters.mp3", "1000meters.mp3", "1500.mp3", "1500meters.mp3",
    "TurnLeft.mp3", "TurnRight.mp3", "KeepLeft.mp3", "KeepRight.mp3",
    "Straight.mp3", "uturn.mp3", "ExitLeft.mp3", "ExitRight.mp3",
    "Roundabout.mp3", "First.mp3", "Second.mp3", "Third.mp3", "Fourth.mp3",
    "Fifth.mp3", "Sixth.mp3", "Seventh.mp3", "AndThen.mp3",
    "ApproachAccident.mp3", "ApproachHazard.mp3", "ApproachSpeedCam.mp3",
    "ApproachRedLightCam.mp3", "ApproachTraffic.mp3", "Police.mp3",
    "Arrive.mp3", "TickerPoints.mp3"
]

RUBBLE_PROMPTS = {
    # StartDrive (9 Varianten mit Paw Patrol & Bauarbeiter-Welpen Flair)
    "StartDrive1.mp3": "Rubble packt an! Hey ho, alle Pfoten an Bord! Schnall dich gut an, dein Bauarbeiter-Welpe ist bereit. Lass uns losbaggern!",
    "StartDrive2.mp3": "Wau wau! Hier ist Rubble! Helm aufgesetzt und Sicherheitsgurt festgezogen! Ich zeig dir den Weg durch die Abenteuerbucht!",
    "StartDrive3.mp3": "Kein Einsatz zu groß, keine Pfote zu klein! Motor starten, Schaufel heben und auf geht's ins nächste Abenteuer!",
    "StartDrive4.mp3": "Bagger bereit, Ketten geölt! Heute bauen wir die schnellste Route überhaupt! Lass uns losrollen!",
    "StartDrive5.mp3": "Wau! Rubble meldet sich zum Dienst! Vor der Fahrt noch schnell ein Hundeleckerli... mmmh, lecker! Und jetzt: Abfahrt!",
    "StartDrive6.mp3": "Auf die Pfoten, fertig, los! Ich halte vom Beifahrersitz aus Ausschau nach Baustellen und freier Fahrt!",
    "StartDrive7.mp3": "Hey du! Schön, dass wir heute zusammen unterwegs sind! Schnall dich an, dein Lieblings-Welpe hat das Navi fest im Griff!",
    "StartDrive8.mp3": "Rubble packt an! Heute schieben wir alle Staus einfach mit der Schaufel zur Seite! Los geht die wilde Fahrt!",
    "StartDrive9.mp3": "Wau wau! Route berechnet! Bagger vollgetankt und Pfoten gewaschen. Bring uns sicher ans Ziel!",

    # Abbiegen & Manöver
    "TurnLeft.mp3": "Hier links abbiegen! Schöne Kurve!",
    "TurnRight.mp3": "Jetzt rechts abbiegen! Genau da lang!",
    "KeepLeft.mp3": "Halt dich bitte links!",
    "KeepRight.mp3": "Halt dich bitte rechts!",
    "Straight.mp3": "Einfach geradeaus weiterrollen!",
    "uturn.mp3": "Halt, stopp! Wir müssen umdrehen! Wende bitte bei nächster Gelegenheit!",
    "ExitLeft.mp3": "Ausfahrt links nehmen!",
    "ExitRight.mp3": "Ausfahrt rechts nehmen!",
    "AndThen.mp3": "Und gleich danach...",

    # Distanzen
    "200meters.mp3": "In zweihundert Metern...",
    "400meters.mp3": "In vierhundert Metern...",
    "800meters.mp3": "In achthundert Metern...",
    "1000meters.mp3": "In einem Kilometer...",
    "1500meters.mp3": "In anderthalb Kilometern...",
    "200.mp3": "In zweihundert Metern...",
    "400.mp3": "In vierhundert Metern...",
    "800.mp3": "In achthundert Metern...",
    "1500.mp3": "In anderthalb Kilometern...",

    # Kreisverkehr
    "Roundabout.mp3": "Fahr in den Kreisverkehr ein...",
    "First.mp3": "Nimm die erste Ausfahrt!",
    "Second.mp3": "Nimm die zweite Ausfahrt!",
    "Third.mp3": "Nimm die dritte Ausfahrt!",
    "Fourth.mp3": "Nimm die vierte Ausfahrt!",
    "Fifth.mp3": "Nimm die fünfte Ausfahrt!",
    "Sixth.mp3": "Nimm die sechste Ausfahrt!",
    "Seventh.mp3": "Nimm die siebte Ausfahrt!",

    # Warnungen & Gefahren
    "ApproachSpeedCam.mp3": "Wau! Achtung, Blitzer voraus! Nimm schnell die Pfote vom Gas, sonst wird das ein teures Hundeleckerli!",
    "ApproachRedLightCam.mp3": "Achtung, Blitzer an der roten Ampel! Schön brav anhalten, wenn's rot wird!",
    "Police.mp3": "Achtung, die Polizei steht da vorne! Chase ist zwar nicht dabei, aber wir halten uns an alle Regeln!",
    "ApproachAccident.mp3": "Vorsicht, weiter vorne gab es einen Unfall! Fahr vorsichtig vorbei!",
    "ApproachHazard.mp3": "Gefahr auf der Fahrbahn gemeldet! Augen auf die Straße!",
    "ApproachTraffic.mp3": "Achtung, da vorne staut es sich! Keine Sorge, Rubble packt an und wir kommen trotzdem durch!",

    # Ziel & Punkte
    "Arrive.mp3": "Juhu, wir haben unser Ziel erreicht! Super gefahren! Zur Belohnung gibt's jetzt für alle einen leckeren Hundekuchen! Wau wau!",
    "TickerPoints.mp3": "Pling! Neue Punkte für die PAW Patrol!"
}

def call_fish_audio_tts(text: str) -> bytes:
    payload = {
        "text": text,
        "reference_id": FISH_MODEL_ID,
        "format": "mp3",
        "mp3_bitrate": 64
    }
    headers = {
        "Authorization": f"Bearer {FISH_API_KEY}",
        "Content-Type": "application/json",
        "model": "s2.1-pro-free"
    }
    for attempt in range(4):
        try:
            resp = requests.post(FISH_API_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 1000:
                return resp.content
            time.sleep(1.5)
        except Exception as e:
            time.sleep(1.5)
    raise RuntimeError(f"Failed to generate TTS for: {text}")

def convert_and_optimize_file(in_path: str, out_path: str, bitrate_kbps: int = 36, volume_boost_db: float = 5.5) -> bool:
    cmd = [
        "ffmpeg", "-y",
        "-i", in_path,
        "-af", f"volume={volume_boost_db}dB,alimiter=limit=0.95",
        "-ar", "44100",
        "-ac", "1",
        "-b:a", f"{bitrate_kbps}k",
        "-c:a", "libmp3lame",
        out_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0

# --- WAZE UPLOADER LOGIC ---
def decode_hex_protobuf(hex_string: str) -> dict:
    message, _ = blackboxprotobuf.protobuf_to_json(base64.b16decode(hex_string, True))
    return json.loads(message)

def encode_to_protobase64(json_data: dict, proto_type: dict) -> str:
    raw_encoded = blackboxprotobuf.encode_message(json_data, proto_type)
    return "ProtoBase64," + str(base64.b64encode(raw_encoded), "utf-8")

def get_folder_size_mb(folder_path: str) -> float:
    total_bytes = 0
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.endswith(".mp3") and f in VALID_WAZE_FILENAMES:
                total_bytes += os.path.getsize(os.path.join(root, f))
    return total_bytes / (1024 * 1024)

def create_waze_tar_gz(pack_folder: str, output_tar_path: str) -> bool:
    with tarfile.open(output_tar_path, "w:gz") as tar:
        for fname in os.listdir(pack_folder):
            if fname.endswith(".mp3") and fname in VALID_WAZE_FILENAMES:
                file_path = os.path.join(pack_folder, fname)
                tar.add(file_path, arcname=fname)
    return True

def get_waze_login_headers():
    for attempt in range(4):
        try:
            uuid1 = str(uuid.uuid4())
            uuid2 = str(uuid.uuid4())
            uuid3 = str(uuid.uuid4())

            main_post_typedef = {
                '1001': {
                    'type': 'message',
                    'message_typedef': {
                        '2184': {
                            'type': 'message',
                            'message_typedef': {
                                '1': {'type': 'int', 'name': ''},
                                '3': {'type': 'bytes', 'name': ''},
                                '5': {'type': 'bytes', 'name': ''},
                                '6': {'type': 'bytes', 'name': ''},
                                '11': {'type': 'bytes', 'name': ''},
                                '16': {'type': 'bytes', 'name': ''},
                                '17': {'type': 'bytes', 'name': ''},
                                '18': {'type': 'int', 'name': ''},
                                '19': {'type': 'int', 'name': ''},
                                '22': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''},
                                '24': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'int', 'name': ''}}, 'name': ''},
                                '25': {'type': 'bytes', 'name': ''},
                                '26': {'type': 'bytes', 'name': ''},
                                '28': {'type': 'int', 'name': ''},
                            },
                            'name': '',
                        }
                    },
                    'name': '',
                }
            }
            second_post_typedef2 = {'1001': {'type': 'message', 'message_typedef': {'2219': {'type': 'message', 'message_typedef': {}, 'name': ''}}, 'name': ''}}
            third_post_typedef2 = {'1001': {'type': 'message', 'message_typedef': {'2744': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'bytes', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}, '4': {'type': 'int', 'name': ''}, '5': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}
            third_post_typedef3 = {'1001': {'type': 'message', 'message_typedef': {'2108': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}

            main_post_data = {
                "1001": {
                    "2184": {
                        "1": 234,
                        "3": "4.106.0.1",
                        "5": "Waydroid",
                        "6": "WayDroid x86_64 Device",
                        "11": "11-SDK30",
                        "16": "en",
                        "17": uuid1,
                        "18": 50,
                        "19": 1,
                        "22": {"1": {"1": "uid_enabled", "2": "true"}},
                        "24": {"1": 2, "2": 1920, "3": 1137},
                        "25": "en",
                        "26": uuid2,
                        "28": int(time.time()),
                    }
                }
            }
            second_post_data2 = {"1001": {"2219": {}}}
            third_post_data2 = {"1001": {"2744": {"1": {"1": "worldDATA", "2": "RANDSTRINGDATA"}, "3": 0, "4": 0, "5": 1}}}
            third_post_data3 = {"1001": {"2108": {"1": uuid3, "2": 1}}}

            sequence_num = 1
            headers = {
                "user-agent": "4.106.0.1",
                "sequence-number": str(sequence_num),
                "x-waze-network-version": "3",
                "x-waze-wait-timeout": "3500",
            }
            cookie_jar = requests.cookies.RequestsCookieJar()

            first_post_data = encode_to_protobase64(main_post_data, main_post_typedef) + "\nGetGeoServerConfig,world,T"
            resp1 = requests.post("https://rt.waze.com/rtserver/distrib/login", data=first_post_data, headers=headers, cookies=cookie_jar, timeout=10)
            resp1.raise_for_status()

            sequence_num += 1
            headers["sequence-number"] = str(sequence_num)

            main_post_data["1001"]["2184"]["28"] = int(time.time())
            second_post_data = encode_to_protobase64(main_post_data, main_post_typedef) + "\n" + encode_to_protobase64(second_post_data2, second_post_typedef2)
            resp2 = requests.post("https://rtproxy-row.waze.com/rtserver/distrib/static", data=second_post_data, headers=headers, cookies=cookie_jar, timeout=10)
            resp2.raise_for_status()
            cookie_jar.update(resp2.cookies)

            resp2_decoded = decode_hex_protobuf(resp2.content.hex())
            anon_username = resp2_decoded["1001"][1]["2220"]["1"]
            anon_password = resp2_decoded["1001"][1]["2220"]["2"]

            sequence_num += 1
            headers["sequence-number"] = str(sequence_num)

            main_post_data["1001"]["2184"]["28"] = int(time.time())
            third_post_data2["1001"]["2744"]["1"]["1"] = anon_username
            third_post_data2["1001"]["2744"]["1"]["2"] = anon_password
            third_post_data3["1001"]["2108"]["1"] = uuid3

            third_post_data = (
                encode_to_protobase64(main_post_data, main_post_typedef) + "\n"
                + encode_to_protobase64(third_post_data2, third_post_typedef2) + "\n"
                + encode_to_protobase64(third_post_data3, third_post_typedef3)
            )
            resp3 = requests.post("https://rtproxy-row.waze.com/rtserver/distrib/login", headers=headers, data=third_post_data, cookies=cookie_jar, timeout=10)
            resp3.raise_for_status()
            cookie_jar.update(resp3.cookies)

            resp3_decoded = decode_hex_protobuf(resp3.content.hex())
            auth_token_main = resp3_decoded["1001"][1]["2745"]["1"]["3"]
            global_server = resp3_decoded["1001"][1]["2745"]["1"]["2"]
            user_id = int(resp3_decoded["1001"][1]["2745"]["1"]["1"])

            binary_user_id = str(bin(user_id)[2:])
            user_id_bytes = [b'12']
            while len(binary_user_id) < 31:
                binary_user_id = "0" + binary_user_id
            first = binary_user_id[:3]
            first = str(hex(int(first, 2))[2:])
            user_id_bytes.append(bytes('0' + first, 'raw_unicode_escape'))
            binary_user_id = binary_user_id[3:]

            for _ in range(1, 5):
                work = binary_user_id[:7]
                result = hex(int("1" + work, 2))[2:]
                user_id_bytes.append(bytes(result, 'raw_unicode_escape'))
                binary_user_id = binary_user_id[7:]

            user_id_bytes.append(b'08')
            user_id_bytes = list(reversed(user_id_bytes))

            raw_user_id_bytes = "".join(chr(int(b, 16)) for b in user_id_bytes).encode("raw_unicode_escape")
            auth_token_len = len(auth_token_main)
            auth_token_len_hex = bytes.fromhex(f"{auth_token_len:02x}")
            auth_token_build = raw_user_id_bytes.decode("raw_unicode_escape") + auth_token_len_hex.decode("latin1") + auth_token_main
            final_uid = base64.b64encode(auth_token_build.encode("raw_unicode_escape")).decode("utf-8")

            sequence_num += 1
            final_headers = {
                "uid": final_uid,
                "user-agent": "4.106.0.1",
                "sequence-number": str(sequence_num),
                "x-waze-network-version": "3",
                "x-waze-wait-timeout": "3500",
            }
            return final_headers, global_server, cookie_jar
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(1.0)

VOICE_DATA_PROTOBUF_TYPE_DEF = {
    '1001': {
        'type': 'message',
        'message_typedef': {
            '2343': {
                'type': 'message',
                'message_typedef': {
                    '2': {
                        'type': 'message',
                        'message_typedef': {
                            '1': {'type': 'bytes', 'name': ''},
                            '2': {'type': 'bytes', 'name': ''},
                            '5': {'type': 'bytes', 'name': ''},
                            '12': {'type': 'int', 'name': ''},
                        },
                        'name': '',
                    },
                    '3': {'type': 'bytes', 'name': ''},
                },
                'name': '',
            }
        },
        'name': '',
    }
}

def upload_to_waze_cloud(pack_dir: Path, pack_name: str) -> dict:
    size_mb = get_folder_size_mb(str(pack_dir))
    print(f"Total Pack size: {size_mb:.3f} MB")
    assert size_mb <= 0.78, f"Too big: {size_mb} MB"

    print("Authenticating with Waze Cloud...")
    headers, global_server, cookie_jar = get_waze_login_headers()

    pack_uuid = str(uuid.uuid4())
    tar_path = pack_dir / "ready.tar.gz"
    create_waze_tar_gz(str(pack_dir), str(tar_path))

    with open(tar_path, "rb") as f:
        tar_bytes = f.read()
    b64_tar = str(base64.b64encode(tar_bytes), "utf-8")

    voice_payload = {
        "1001": {
            "2343": {
                "2": {
                    "1": bytes(pack_uuid, "utf-8"),
                    "2": bytes(pack_name, "utf-8"),
                    "5": bytes(global_server, "utf-8") if isinstance(global_server, str) else global_server,
                    "12": 0,
                },
                "3": tar_bytes,
            }
        }
    }
    body = encode_to_protobase64(voice_payload, VOICE_DATA_PROTOBUF_TYPE_DEF)
    upload_url = "https://rtproxy-row.waze.com/rtserver/distrib/command"

    print(f"Uploading to {upload_url} with UUID {pack_uuid}...")
    resp = requests.post(
        upload_url,
        headers=headers,
        data=body,
        cookies=cookie_jar,
        timeout=30
    )
    resp.raise_for_status()

    waze_link = f"https://waze.com/ul?acvp={pack_uuid}"
    download_url = f"https://voice-prompts-ipv6.waze.com/{pack_uuid}.tar.gz"

    result = {
        "name": "Paw Patrol: Rubble",
        "slug": "paw-patrol-rubble",
        "language": "German",
        "country_code": "DE",
        "category": "Cartoons & Kinder",
        "waze_link": waze_link,
        "download_url": download_url,
        "uuid": pack_uuid,
        "file_size_mb": round(size_mb, 3),
        "prompts_count": 43,
        "status": "Active",
        "author": "German Waze Community",
        "sample_line": "Rubble packt an! Hey ho, alle Pfoten an Bord! Schnall dich gut an, dein Bauarbeiter-Welpe ist bereit. Lass uns losbaggern!"
    }
    print("Upload successful!")
    print(f"Waze Link: {waze_link}")
    return result

def main():
    print(f"=== Starte Generierung von {len(VALID_WAZE_FILENAMES)} Prompts mit Rubble (Ivo Möller): {FISH_MODEL_ID} ===")
    success_count = 0
    total_opt_bytes = 0

    for idx, fn in enumerate(VALID_WAZE_FILENAMES, 1):
        text = RUBBLE_PROMPTS.get(fn)
        if not text:
            continue

        raw_path = TEMP_RAW_DIR / fn
        opt_path = OUTPUT_PACK_DIR / fn

        if opt_path.exists() and opt_path.stat().st_size > 1000:
            opt_sz = opt_path.stat().st_size
            total_opt_bytes += opt_sz
            success_count += 1
            print(f" [Cached opt: {opt_sz//1024}KB]")
            continue

        if not raw_path.exists() or raw_path.stat().st_size < 1000:
            try:
                audio_bytes = call_fish_audio_tts(text)
                with open(raw_path, "wb") as f:
                    f.write(audio_bytes)
                print(f" TTS OK ->", end="", flush=True)
            except Exception as e:
                print(f" TTS FEHLER: {e}")
                continue
        else:
            print(f" [Cached raw] ->", end="", flush=True)

        ok = convert_and_optimize_file(str(raw_path), str(opt_path), bitrate_kbps=36, volume_boost_db=5.5)
        if ok and opt_path.exists():
            opt_sz = opt_path.stat().st_size
            total_opt_bytes += opt_sz
            print(f" Opt OK ({opt_sz//1024}KB)")
            success_count += 1
        else:
            print(f" FFmpeg FEHLER!")

        time.sleep(0.5)

    print(f"\nGeneriert: {success_count}/{len(VALID_WAZE_FILENAMES)}, Gesamtgröße: {total_opt_bytes / 1024 / 1024:.3f} MB")

    # Upload to Waze Cloud
    meta = upload_to_waze_cloud(OUTPUT_PACK_DIR, "PawPatrolRubble")
    
    with open(WORKSPACE_DIR / "tools" / "rubble_waze_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print("ALL DONE SUCCESSFULLY!")

if __name__ == "__main__":
    main()
