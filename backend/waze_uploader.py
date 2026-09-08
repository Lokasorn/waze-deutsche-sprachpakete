"""
Waze Cloud Uploader Module.
Implements the reverse-engineered Waze Protocol Buffer authentication and upload pipeline
to publish custom soundpacks directly to Waze servers, generating a public deep-link:
https://waze.com/ul?acvp=<UUID>
"""

import base64
import json
import os
import sys
import tarfile
import time
import uuid
from typing import Dict, Optional, Tuple

import blackboxprotobuf
import requests

from backend.audio_processor import compress_pack_to_limit, create_waze_tar_gz, get_folder_size_mb


def decode_hex_protobuf(hex_string: str) -> dict:
    """Decode hex-encoded Protocol Buffer to JSON."""
    message, _ = blackboxprotobuf.protobuf_to_json(base64.b16decode(hex_string, True))
    return json.loads(message)


def encode_to_protobase64(json_data: dict, proto_type: dict) -> str:
    """Encode JSON data to Protocol Buffer and Base64."""
    raw_encoded = blackboxprotobuf.encode_message(json_data, proto_type)
    return "ProtoBase64," + str(base64.b64encode(raw_encoded), "utf-8")


def get_waze_login_headers() -> Tuple[dict, str, requests.cookies.RequestsCookieJar]:
    """Authenticate anonymously with Waze and return (headers, global_server, cookie_jar)."""
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

    # Step 1: Initial geo server config login
    first_post_data = encode_to_protobase64(main_post_data, main_post_typedef) + "\nGetGeoServerConfig,world,T"
    resp1 = requests.post("https://rt.waze.com/rtserver/distrib/login", data=first_post_data, headers=headers, cookies=cookie_jar, timeout=10)
    resp1.raise_for_status()

    sequence_num += 1
    headers["sequence-number"] = str(sequence_num)

    # Step 2: Anonymous user registration
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

    # Step 3: Distribution server login
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

    # Build UID binary structure
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


def upload_soundpack_to_waze(pack_name: str, pack_folder: str) -> Dict[str, Any]:
    """
    Uploads a soundpack folder to Waze cloud servers.
    Compresses if necessary to ensure <= 0.79 MB.
    Returns a dictionary with status, pack_uuid, and direct waze deep link.
    """
    if not os.path.exists(pack_folder):
        return {"success": False, "error": f"Pack-Ordner existiert nicht: {pack_folder}"}

    # Step 1: Ensure total size is under 0.79 MB
    current_size = get_folder_size_mb(pack_folder)
    if current_size > 0.79:
        print(f"Pack {pack_name} hat {current_size:.2f} MB - komprimiere auf <= 0.78 MB...")
        success, final_size, br = compress_pack_to_limit(pack_folder, target_max_mb=0.78)
        if not success:
            return {"success": False, "error": f"Kompression fehlgeschlagen: {final_size:.2f} MB überschreitet das 0.8 MB Limit."}

    # Step 2: Authenticate with Waze
    try:
        headers, global_server, cookie_jar = get_waze_login_headers()
    except Exception as e:
        return {"success": False, "error": f"Waze Login-Fehler: {str(e)}"}

    pack_uuid = str(uuid.uuid4())
    tar_path = os.path.join(pack_folder, "ready.tar.gz")

    try:
        create_waze_tar_gz(pack_folder, tar_path)
        with open(tar_path, "rb") as f:
            tar_bytes = f.read()
    except Exception as e:
        return {"success": False, "error": f"Fehler beim Erstellen des Archivs: {str(e)}"}
    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)

    # Step 3: Build Protobuf payload
    voice_data = {
        '1001': {
            '2343': {
                '2': {
                    '1': bytes(pack_uuid, "utf-8"),
                    '2': bytes(pack_name, "utf-8"),
                    '5': bytes(global_server, "utf-8") if isinstance(global_server, str) else global_server,
                    '12': 0,
                },
                '3': tar_bytes,
            }
        }
    }

    try:
        encoded_payload = encode_to_protobase64(voice_data, VOICE_DATA_PROTOBUF_TYPE_DEF)
        upload_url = "https://rtproxy-row.waze.com/rtserver/distrib/command"
        upload_resp = requests.post(upload_url, headers=headers, data=encoded_payload, cookies=cookie_jar, timeout=25)
        upload_resp.raise_for_status()
    except Exception as e:
        return {"success": False, "error": f"Upload zum Waze-Server fehlgeschlagen: {str(e)}"}

    deep_link = f"https://waze.com/ul?acvp={pack_uuid}"
    download_link = f"https://voice-prompts-ipv6.waze.com/{pack_uuid}.tar.gz"

    return {
        "success": True,
        "pack_name": pack_name,
        "pack_uuid": pack_uuid,
        "deep_link": deep_link,
        "download_link": download_link,
        "size_mb": round(get_folder_size_mb(pack_folder), 3),
    }
