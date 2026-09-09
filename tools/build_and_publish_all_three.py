import base64
import json
import os
import shutil
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
FISH_API_KEY = "sk-fish-ngV4tP1Ft-2VAwa6xeG3grjEvoA0bGn6PULhtY1S2rM"
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
    "StartDrive1.mp3": "Rubble packt an! Hey ho, alle Pfoten an Bord! Schnall dich gut an, dein Bauarbeiter-Welpe ist bereit. Lass uns losbaggern!",
    "StartDrive2.mp3": "Wau wau! Hier ist Rubble! Helm aufgesetzt und Sicherheitsgurt festgezogen! Ich zeig dir den Weg durch die Abenteuerbucht!",
    "StartDrive3.mp3": "Kein Einsatz zu groß, keine Pfote zu klein! Motor starten, Schaufel heben und auf geht's ins nächste Abenteuer!",
    "StartDrive4.mp3": "Bagger bereit, Ketten geölt! Heute bauen wir die schnellste Route überhaupt! Lass uns losrollen!",
    "StartDrive5.mp3": "Wau! Rubble meldet sich zum Dienst! Vor der Fahrt noch schnell ein Hundeleckerli... mmmh, lecker! Und jetzt: Abfahrt!",
    "StartDrive6.mp3": "Auf die Pfoten, fertig, los! Ich halte vom Beifahrersitz aus Ausschau nach Baustellen und freier Fahrt!",
    "StartDrive7.mp3": "Hey du! Schön, dass wir heute zusammen unterwegs sind! Schnall dich an, dein Lieblings-Welpe hat das Navi fest im Griff!",
    "StartDrive8.mp3": "Rubble packt an! Heute schieben wir alle Staus einfach mit der Schaufel zur Seite! Los geht die wilde Fahrt!",
    "StartDrive9.mp3": "Wau wau! Route berechnet! Bagger vollgetankt und Pfoten gewaschen. Bring uns sicher ans Ziel!",

    "TurnLeft.mp3": "Wau! Hier links abbiegen!",
    "TurnRight.mp3": "Wau! Jetzt rechts abbiegen!",
    "KeepLeft.mp3": "Halt dich links, Wau wau!",
    "KeepRight.mp3": "Halt dich rechts, Wau wau!",
    "Straight.mp3": "Geradeaus weiterbaggern!",
    "uturn.mp3": "Halt, stopp! Wende bitte bei nächster Gelegenheit!",
    "ExitLeft.mp3": "Ausfahrt links nehmen, Wau!",
    "ExitRight.mp3": "Ausfahrt rechts nehmen, Wau!",
    "AndThen.mp3": "Und gleich danach...",

    "200meters.mp3": "Wau! In zweihundert Metern...",
    "400meters.mp3": "Wau! In vierhundert Metern...",
    "800meters.mp3": "Wau! In achthundert Metern...",
    "1000meters.mp3": "Wau! In einem Kilometer...",
    "1500meters.mp3": "Wau! In anderthalb Kilometern...",
    "200.mp3": "Wau! In zweihundert Metern...",
    "400.mp3": "Wau! In vierhundert Metern...",
    "800.mp3": "Wau! In achthundert Metern...",
    "1500.mp3": "Wau! In anderthalb Kilometern...",

    "Roundabout.mp3": "Fahr in den Kreisverkehr ein, Wau!",
    "First.mp3": "Nimm die erste Ausfahrt, Wau wau!",
    "Second.mp3": "Nimm die zweite Ausfahrt, Wau wau!",
    "Third.mp3": "Nimm die dritte Ausfahrt, Wau wau!",
    "Fourth.mp3": "Nimm die vierte Ausfahrt, Wau wau!",
    "Fifth.mp3": "Nimm die fünfte Ausfahrt, Wau wau!",
    "Sixth.mp3": "Nimm die sechste Ausfahrt, Wau wau!",
    "Seventh.mp3": "Nimm die siebte Ausfahrt, Wau wau!",

    "ApproachSpeedCam.mp3": "Wau! Achtung, Blitzer voraus! Nimm schnell die Pfote vom Gas, sonst wird das ein teures Hundeleckerli!",
    "ApproachRedLightCam.mp3": "Achtung, Blitzer an der roten Ampel! Schön brav anhalten, wenn's rot wird!",
    "Police.mp3": "Achtung, die Polizei steht da vorne! Chase ist zwar nicht dabei, aber wir halten uns an alle Regeln!",
    "ApproachAccident.mp3": "Vorsicht, weiter vorne gab es einen Unfall! Fahr vorsichtig vorbei!",
    "ApproachHazard.mp3": "Gefahr auf der Fahrbahn gemeldet! Augen auf die Straße!",
    "ApproachTraffic.mp3": "Achtung, da vorne staut es sich! Keine Sorge, Rubble packt an und wir kommen trotzdem durch!",

    "Arrive.mp3": "Juhu, wir haben unser Ziel erreicht! Super gefahren! Zur Belohnung gibt's jetzt für alle einen leckeren Hundekuchen! Wau wau!",
    "TickerPoints.mp3": "Wau! Neue Punkte für die PAW Patrol!"
}

SPONGEBOB_PROMPTS = {
    "StartDrive1.mp3": "Hahahahaha! Ich bin bereit, ich bin bereit, ich bin bereit! Schnall dich an, Kumpel! Wir machen heute die Straßen von Bikini Bottom unsicher! Abfahrt!",
    "StartDrive2.mp3": "Guten Morgen Bikini Bottom! Schalte den Motor an und vergiss deinen Sicherheitsgurt nicht! Auf zum Quallenfischen!",
    "StartDrive3.mp3": "Hahaha! Heute ist der beste Tag überhaupt! Gary hat schon gefressen, also lass uns losdüsen!",
    "StartDrive4.mp3": "Achtung, jetzt kommt das schnellste Bootmobil im ganzen Ozean! Volle Fahrt voraus!",
    "StartDrive5.mp3": "Ich bin bereit! Schnall dich an, Kumpel, bevor Mrs. Puff uns erwischt! Hahahahaha!",
    "StartDrive6.mp3": "Auf geht's! Eine Runde durch Bikini Bottom und danach gibt's für alle leckere Krabbenburger!",
    "StartDrive7.mp3": "Bereit machen zum Ausparken! Nach vorne... und noch ein Stück... Perfekt! Los geht's!",
    "StartDrive8.mp3": "Hahaha, ich liebe Autofahren! Na ja, zumindest solange ich nicht durch die Fahrprüfung falle! Ab geht die Post!",
    "StartDrive9.mp3": "Juhu! Navigation gestartet! Ich zeige dir den allerbesten Weg, versprochen!",

    "TurnLeft.mp3": "Hier links abbiegen!",
    "TurnRight.mp3": "Jetzt rechts abbiegen!",
    "KeepLeft.mp3": "Halt dich links!",
    "KeepRight.mp3": "Halt dich schön rechts!",
    "Straight.mp3": "Einfach geradeaus weiterdüsen!",
    "uturn.mp3": "Umdrehen, umdrehen! Wende bitte bei nächster Gelegenheit!",
    "ExitLeft.mp3": "Nimm die Ausfahrt links!",
    "ExitRight.mp3": "Nimm die Ausfahrt rechts!",
    "AndThen.mp3": "Und gleich danach...",

    "200meters.mp3": "In zweihundert Metern...",
    "400meters.mp3": "In vierhundert Metern...",
    "800meters.mp3": "In achthundert Metern...",
    "1000meters.mp3": "In einem Kilometer...",
    "1500meters.mp3": "In anderthalb Kilometern...",
    "200.mp3": "In zweihundert Metern...",
    "400.mp3": "In vierhundert Metern...",
    "800.mp3": "In achthundert Metern...",
    "1500.mp3": "In anderthalb Kilometern...",

    "Roundabout.mp3": "Fahr in den Kreisverkehr ein...",
    "First.mp3": "Nimm die erste Ausfahrt!",
    "Second.mp3": "Nimm die zweite Ausfahrt!",
    "Third.mp3": "Nimm die dritte Ausfahrt!",
    "Fourth.mp3": "Nimm die vierte Ausfahrt!",
    "Fifth.mp3": "Nimm die fünfte Ausfahrt!",
    "Sixth.mp3": "Nimm die sechste Ausfahrt!",
    "Seventh.mp3": "Nimm die siebte Ausfahrt!",

    "ApproachSpeedCam.mp3": "Wooohoo! Langsamer, fahr langsamer! Da vorne steht ein Blitzer! Wenn Mrs. Puff das sieht, krieg ich meinen Führerschein nie!",
    "ApproachRedLightCam.mp3": "Achtung, Rote-Ampel-Blitzer voraus! Schön brav anhalten, wenn's rot wird!",
    "Police.mp3": "Oh oh! Die Unterwasser-Polizei steht da vorne! Schön artig winken und langsam fahren!",
    "ApproachAccident.mp3": "Vorsicht, weiter vorne gab's einen Unfall! Fahr vorsichtig vorbei!",
    "ApproachHazard.mp3": "Gefahr auf der Fahrbahn gemeldet! Halt die Augen offen!",
    "ApproachTraffic.mp3": "Oh nein, ein Stau! Da stehen wohl ein paar Quallen im Weg! Hab Geduld!",

    "Arrive.mp3": "Juhu, wir haben unser Ziel erreicht! Hahahahaha! Das war eine super Fahrt! Jetzt hab ich Hunger auf einen Krabbenburger!",
    "TickerPoints.mp3": "Juhu! Neue Waze-Punkte für uns! Hahaha!"
}

THADDAEUS_PROMPTS = {
    "StartDrive1.mp3": "Seufz... Muss das denn wirklich sein? Na schön. Zünd den Motor an und fahr einfach ganz ruhig los, damit ich in Ruhe meine Klarinette üben kann.",
    "StartDrive2.mp3": "Guten Tag. Bitte fahr einfach ordentlich und ohne alberne Witze. Ich möchte einfach nur pünktlich ankommen.",
    "StartDrive3.mp3": "Schon wieder eine Autofahrt mit Amateuren. Schnall dich gefälligst an und fahr vorsichtig.",
    "StartDrive4.mp3": "Ich hasse Montage, ich hasse Staus, und ich hasse schlechte Autofahrer. Enttäusch mich bitte nicht. Fahr los.",
    "StartDrive5.mp3": "Seufz... Wenn SpongeBob gleich wieder auftaucht, gebe ich Gas. Bitte bring mich einfach in einem Stück ans Ziel.",
    "StartDrive6.mp3": "Motor an, Radio aus. Ich brauche absolute Ruhe für meine musikalische Inspiration. Fahr los.",
    "StartDrive7.mp3": "Geduld ist eine Tugend, die ich leider nicht besitze. Fahr zügig, aber ohne Knöllchen zu kassieren.",
    "StartDrive8.mp3": "Heute streike ich innerlich sowieso schon. Bring uns einfach schnell an den Zielort.",
    "StartDrive9.mp3": "Hier spricht dein anspruchsvoller Beifahrer. Fahr bitte ruhig und kultiviert. Abfahrt.",

    "TurnLeft.mp3": "Hier links abbiegen.",
    "TurnRight.mp3": "Jetzt rechts abbiegen.",
    "KeepLeft.mp3": "Halt dich links.",
    "KeepRight.mp3": "Halt dich rechts.",
    "Straight.mp3": "Einfach geradeaus weiterfahren.",
    "uturn.mp3": "Halt, falsch! Bitte bei nächster Gelegenheit umdrehen!",
    "ExitLeft.mp3": "Die Ausfahrt links nehmen.",
    "ExitRight.mp3": "Die Ausfahrt rechts nehmen.",
    "AndThen.mp3": "Und direkt danach...",

    "200meters.mp3": "In zweihundert Metern...",
    "400meters.mp3": "In vierhundert Metern...",
    "800meters.mp3": "In achthundert Metern...",
    "1000meters.mp3": "In einem Kilometer...",
    "1500meters.mp3": "In anderthalb Kilometern...",
    "200.mp3": "In zweihundert Metern...",
    "400.mp3": "In vierhundert Metern...",
    "800.mp3": "In achthundert Metern...",
    "1500.mp3": "In anderthalb Kilometern...",

    "Roundabout.mp3": "In den Kreisverkehr einfahren...",
    "First.mp3": "Die erste Ausfahrt nehmen.",
    "Second.mp3": "Die zweite Ausfahrt nehmen.",
    "Third.mp3": "Die dritte Ausfahrt nehmen.",
    "Fourth.mp3": "Die vierte Ausfahrt nehmen.",
    "Fifth.mp3": "Die fünfte Ausfahrt nehmen.",
    "Sixth.mp3": "Die sechste Ausfahrt nehmen.",
    "Seventh.mp3": "Die siebte Ausfahrt nehmen.",

    "ApproachSpeedCam.mp3": "Achtung. Da vorne steht ein Blitzer. Brems gefälligst ab, ich habe keine Lust, mein hart verdientes Geld an die Stadt zu verschwenden.",
    "ApproachRedLightCam.mp3": "Achtung, Ampelblitzer voraus. Nicht bei Gelb drüberrasen, bleib stehen.",
    "Police.mp3": "Achtung, die Polizei steht da vorne. Schön brav das Tempolimit einhalten.",
    "ApproachAccident.mp3": "Vorsicht, da vorne gab es einen Unfall. Fahr vorsichtig vorbei.",
    "ApproachHazard.mp3": "Gefahr auf der Fahrbahn. Pass gefälligst auf.",
    "ApproachTraffic.mp3": "Großartig, ein Stau. Genau das hat mir heute noch gefehlt. Seufz...",

    "Arrive.mp3": "Endlich angekommen. Ich dachte schon, diese Tortur nimmt nie ein Ende. Jetzt brauche ich erstmal ein heißes Schaumbad.",
    "TickerPoints.mp3": "Pling. Schon wieder irgendwelche Punkte. Wie faszinierend..."
}

PACKS_CONFIG = [
    {
        "name": "Paw Patrol: Rubble",
        "slug": "paw-patrol-rubble",
        "folder_name": "PawPatrolRubble",
        "model_id": "0914c177af5a4b59aadb3e670acd56d1",
        "category": "Cartoons & Kinder",
        "prompts": RUBBLE_PROMPTS,
        "sample_line": "Rubble packt an! Hey ho, alle Pfoten an Bord! Schnall dich gut an, dein Bauarbeiter-Welpe ist bereit. Lass uns losbaggern!"
    },
    {
        "name": "SpongeBob Schwammkopf",
        "slug": "spongebob-schwammkopf",
        "folder_name": "SpongeBobSchwammkopf",
        "model_id": "5ea97971497248e085ead9fad68f4011",
        "category": "Cartoons & Kinder",
        "prompts": SPONGEBOB_PROMPTS,
        "sample_line": "Hahahahaha! Ich bin bereit, ich bin bereit, ich bin bereit! Schnall dich an, Kumpel! Wir machen heute die Straßen von Bikini Bottom unsicher! Abfahrt!"
    },
    {
        "name": "Thaddäus Tentakel",
        "slug": "thaddaeus-tentakel",
        "folder_name": "ThaddaeusTentakel",
        "model_id": "8d1e3f20f3af41649511dc2434919c98",
        "category": "Cartoons & Kinder",
        "prompts": THADDAEUS_PROMPTS,
        "sample_line": "Seufz... Muss das denn wirklich sein? Na schön. Zünd den Motor an und fahr einfach ganz ruhig los, damit ich in Ruhe meine Klarinette üben kann."
    }
]

def call_fish_audio_tts(text: str, model_id: str) -> bytes:
    payload = {
        "text": text,
        "reference_id": model_id,
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
            print(f"[Retry {attempt+1}] Status: {resp.status_code} ({len(resp.content)}b) - {resp.text[:60]}")
            time.sleep(2.0)
        except Exception as e:
            print(f"[Retry {attempt+1}] Exception: {e}")
            time.sleep(2.0)
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

# --- WAZE PROTOBUF UPLOADER (Exact working handshake) ---
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
        for fname in sorted(os.listdir(pack_folder)):
            if fname.endswith(".mp3") and fname in VALID_WAZE_FILENAMES:
                file_path = os.path.join(pack_folder, fname)
                tar.add(file_path, arcname=fname)
    return True

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
            resp1 = requests.post("https://rt.waze.com/rtserver/distrib/login", data=first_post_data, headers=headers, cookies=cookie_jar, timeout=12)
            resp1.raise_for_status()

            sequence_num += 1
            headers["sequence-number"] = str(sequence_num)

            main_post_data["1001"]["2184"]["28"] = int(time.time())
            second_post_data = encode_to_protobase64(main_post_data, main_post_typedef) + "\n" + encode_to_protobase64(second_post_data2, second_post_typedef2)
            resp2 = requests.post("https://rtproxy-row.waze.com/rtserver/distrib/static", data=second_post_data, headers=headers, cookies=cookie_jar, timeout=12)
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
            resp3 = requests.post("https://rtproxy-row.waze.com/rtserver/distrib/login", headers=headers, data=third_post_data, cookies=cookie_jar, timeout=12)
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
            print(f"[Waze Auth Attempt {attempt+1}] Error: {e}")
            if attempt == 3:
                raise
            time.sleep(1.5)

def upload_to_waze_cloud(pack_dir: Path, pack_name: str) -> dict:
    size_mb = get_folder_size_mb(str(pack_dir))
    print(f"\n[Waze Cloud] Total Pack size: {size_mb:.3f} MB")
    assert size_mb <= 0.78, f"Too big: {size_mb} MB"

    print("Authenticating with Waze Cloud...")
    headers, global_server, cookie_jar = get_waze_login_headers()

    pack_uuid = str(uuid.uuid4())
    tar_path = pack_dir.parent / f"{pack_name}_upload.tar.gz"
    create_waze_tar_gz(str(pack_dir), str(tar_path))

    with open(tar_path, "rb") as f:
        tar_bytes = f.read()

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

    print(f"Uploading {pack_name} ({pack_uuid}) to Waze Cloud...")
    resp = requests.post(upload_url, headers=headers, data=body, cookies=cookie_jar, timeout=40)
    resp.raise_for_status()

    waze_link = f"https://waze.com/ul?acvp={pack_uuid}"
    download_url = f"https://voice-prompts-ipv6.waze.com/{pack_uuid}.tar.gz"

    # Verify download URL
    time.sleep(1.0)
    dl_resp = requests.get(download_url, timeout=15)
    print(f"Verified Waze Cloud Download URL: HTTP {dl_resp.status_code} ({len(dl_resp.content)} bytes)")

    if tar_path.exists():
        tar_path.unlink()

    return {
        "uuid": pack_uuid,
        "waze_link": waze_link,
        "download_url": download_url,
        "size_mb": round(size_mb, 3)
    }

def create_verify_html(pack_dir: Path, title: str, sample_line: str):
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Verifikation: {title} (Alle 43 Waze-Prompts)</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;800&family=Plus+Jakarta+Sans:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {{ background: #0b132b; color: #f1f5f9; font-family: 'Plus Jakarta Sans', sans-serif; padding: 40px 20px; }}
    .container {{ max-width: 1000px; margin: 0 auto; }}
    h1 {{ font-family: 'Outfit', sans-serif; font-size: 32px; color: #38bdf8; margin-bottom: 8px; }}
    p.lead {{ color: #94a3b8; margin-bottom: 24px; }}
    .sample-banner {{ background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 16px; margin-bottom: 30px; font-style: italic; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }}
    .card {{ background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px; }}
    .card-title {{ font-weight: 700; font-size: 13.5px; margin-bottom: 8px; color: #e2e8f0; font-family: monospace; }}
    audio {{ width: 100%; height: 32px; }}
  </style>
</head>
<body>
<div class="container">
  <h1>🔊 {title}</h1>
  <p class="lead">Vollständige Überprüfung aller 43 standardisierten Waze-Audiodateien (44.1 kHz Mono Studio-Mastering).</p>
  <div class="sample-banner">„{sample_line}“</div>
  <div class="grid">
"""
    for fn in VALID_WAZE_FILENAMES:
        html += f"""    <div class="card">
      <div class="card-title">{fn}</div>
      <audio controls preload="none" src="{fn}"></audio>
    </div>\n"""
    html += """  </div>
</div>
</body>
</html>"""
    with open(pack_dir / "verify_all.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    print("==================================================================")
    print(" BATCH BUILD & PUBLISH: Rubble, SpongeBob & Thaddäus (43 Prompts) ")
    print("==================================================================")

    published_file = WORKSPACE_DIR / "tools" / "published_three_packs.json"
    published_packs = {}
    if published_file.exists():
        try:
            with open(published_file, "r", encoding="utf-8") as f:
                published_packs = json.load(f)
        except:
            published_packs = {}

    for cfg in PACKS_CONFIG:
        name = cfg["name"]
        slug = cfg["slug"]
        folder = cfg["folder_name"]
        model_id = cfg["model_id"]
        prompts = cfg["prompts"]
        sample_line = cfg["sample_line"]

        print(f"\n==================================================")
        print(f" PROCESSING: {name} ({slug})")
        print(f" Model ID: {model_id}")
        print(f"==================================================")

        pack_dir = WORKSPACE_DIR / "packs" / folder
        pack_dir.mkdir(parents=True, exist_ok=True)
        raw_dir = WORKSPACE_DIR / "tools" / f"raw_43_{slug}"
        raw_dir.mkdir(parents=True, exist_ok=True)

        generated_count = 0
        total_bytes = 0

        for fn in VALID_WAZE_FILENAMES:
            text = prompts.get(fn)
            if not text:
                continue

            raw_path = raw_dir / fn
            opt_path = pack_dir / fn

            if opt_path.exists() and opt_path.stat().st_size > 1000:
                sz = opt_path.stat().st_size
                total_bytes += sz
                generated_count += 1
                continue

            if not raw_path.exists() or raw_path.stat().st_size < 1000:
                try:
                    audio_bytes = call_fish_audio_tts(text, model_id)
                    with open(raw_path, "wb") as f:
                        f.write(audio_bytes)
                    print(f"  [TTS OK] {fn} ({len(audio_bytes)}b) ->", end="", flush=True)
                except Exception as e:
                    print(f"  [TTS FAILED] {fn}: {e}")
                    continue
            else:
                print(f"  [Cached raw] {fn} ->", end="", flush=True)

            ok = convert_and_optimize_file(str(raw_path), str(opt_path), bitrate_kbps=36, volume_boost_db=5.5)
            if ok and opt_path.exists():
                sz = opt_path.stat().st_size
                total_bytes += sz
                generated_count += 1
                print(f" [Car Master OK: {sz//1024}KB]")
            else:
                print(f" [Car Master FAILED]")
            time.sleep(0.3)

        print(f"\nSuccessfully verified/generated {generated_count}/43 prompts for {name} ({total_bytes / 1024 / 1024:.3f} MB)")
        create_verify_html(pack_dir, name, sample_line)

        # Upload to Waze Cloud
        cloud_meta = upload_to_waze_cloud(pack_dir, name)
        published_packs[slug] = {
            "name": name,
            "slug": slug,
            "folder_name": folder,
            "language": "German",
            "country_code": "DE",
            "category": cfg["category"],
            "waze_link": cloud_meta["waze_link"],
            "download_url": cloud_meta["download_url"],
            "uuid": cloud_meta["uuid"],
            "file_size_mb": cloud_meta["size_mb"],
            "prompts_count": 43,
            "status": "Active",
            "author": "German Waze Community",
            "sample_line": sample_line
        }

        with open(published_file, "w", encoding="utf-8") as f:
            json.dump(published_packs, f, indent=2, ensure_ascii=False)

    print("\nALL 3 SOUNDPACKS BUILT AND UPLOADED TO WAZE CLOUD SUCCESSFULLY!")

if __name__ == "__main__":
    main()
