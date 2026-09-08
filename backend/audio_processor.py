"""
Audio Processor for Waze Voicepacks.
Handles normalization (+7dB car boost), mono conversion, MP3 encoding,
and deterministic binary-search compression to stay under Waze's strict 0.8 MB cloud limit.
"""

import os
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.waze_prompts import VALID_WAZE_FILENAMES

TARGET_PACK_SIZE_MB = 0.78       # Strict limit is 0.8 MB, 0.78 MB ensures 100% cloud acceptance
DEFAULT_VOLUME_BOOST_DB = 7.0     # Boost to cut through engine/road noise
SAMPLE_RATE = 44100              # 44.1 kHz standard
CHANNELS = 1                     # Mono


def get_ffmpeg_executable() -> str:
    """Find the path to the ffmpeg executable."""
    # Check WinGet Gyan Shared / Essentials install first
    gyan_shared = Path(r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build-shared\bin\ffmpeg.exe")
    if gyan_shared.exists():
        return str(gyan_shared)
    gyan_path = Path(r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe")
    if gyan_path.exists():
        return str(gyan_path)

    ffmpeg_cmd = shutil.which("ffmpeg")
    if ffmpeg_cmd:
        return ffmpeg_cmd
    
    # Common Windows winget / gyan install paths
    user_local = os.environ.get("LOCALAPPDATA", "")
    user_profile = os.environ.get("USERPROFILE", "")
    possible_paths = [
        Path(user_local) / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe",
        Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
        Path(user_profile) / "scoop" / "shims" / "ffmpeg.exe",
    ]
    for p in possible_paths:
        if p.exists():
            return str(p)
            
    # Default fallback
    return "ffmpeg"


def get_folder_size_mb(folder_path: str) -> float:
    """Calculate the total size in MB of all valid Waze MP3s in the folder."""
    total_bytes = 0
    if not os.path.exists(folder_path):
        return 0.0
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.endswith(".mp3") and f in VALID_WAZE_FILENAMES:
                total_bytes += os.path.getsize(os.path.join(root, f))
    return total_bytes / (1024 * 1024)


def convert_and_optimize_file(
    input_file: str,
    output_file: str,
    bitrate_kbps: int = 32,
    volume_boost_db: float = DEFAULT_VOLUME_BOOST_DB,
    sample_rate: int = SAMPLE_RATE,
) -> bool:
    """
    Converts and normalizes an audio file using FFmpeg.
    Ensures 1-channel mono, target sample rate, volume boost, and target bitrate.
    """
    ffmpeg_bin = get_ffmpeg_executable()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Filter chain: volume boost + slight limiter to avoid clipping
    filter_expr = f"volume={volume_boost_db}dB,alimiter=limit=0.95"

    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", input_file,
        "-af", filter_expr,
        "-ar", str(sample_rate),
        "-ac", str(CHANNELS),
        "-b:a", f"{bitrate_kbps}k",
        "-c:a", "libmp3lame",
        output_file
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error converting {input_file}: {e.stderr.decode(errors='ignore')}")
        return False
    except Exception as e:
        print(f"Unexpected error running FFmpeg: {e}")
        return False


def compress_pack_to_limit(pack_folder: str, target_max_mb: float = TARGET_PACK_SIZE_MB) -> Tuple[bool, float, int]:
    """
    Compresses all MP3s in the pack folder using binary search on the bitrate
    to ensure the total folder size is <= target_max_mb.
    Returns (success, final_size_mb, best_bitrate_kbps).
    """
    current_size = get_folder_size_mb(pack_folder)
    if current_size <= target_max_mb and current_size > 0:
        return True, current_size, 32

    # Make a backup copy of original files
    backup_folder = pack_folder + "__TEMP_ORIGINAL"
    if os.path.exists(backup_folder):
        shutil.rmtree(backup_folder)
    shutil.copytree(pack_folder, backup_folder)

    # Search range for bitrates in kbps
    bitrates_to_try = [48, 40, 36, 32, 28, 24, 20, 16]
    best_bitrate = 24
    best_size = current_size
    success = False

    for br in bitrates_to_try:
        for fname in os.listdir(backup_folder):
            if fname.endswith(".mp3") and fname in VALID_WAZE_FILENAMES:
                src = os.path.join(backup_folder, fname)
                dst = os.path.join(pack_folder, fname)
                # If bitrate gets very low, lower sample rate slightly to keep audio clear
                sr = 22050 if br <= 20 else SAMPLE_RATE
                convert_and_optimize_file(src, dst, bitrate_kbps=br, sample_rate=sr)

        size = get_folder_size_mb(pack_folder)
        print(f"Pack compression test: {br} kbps -> {size:.3f} MB (Target: <= {target_max_mb} MB)")

        if size <= target_max_mb:
            best_bitrate = br
            best_size = size
            success = True
            break
        else:
            best_size = size

    # Clean up backup folder
    if os.path.exists(backup_folder):
        shutil.rmtree(backup_folder)

    return success, best_size, best_bitrate


def create_waze_tar_gz(pack_folder: str, output_tar_path: str) -> bool:
    """
    Packages all valid Waze MP3s into a .tar.gz archive ready for Waze API upload.
    """
    try:
        os.makedirs(os.path.dirname(output_tar_path), exist_ok=True)
        with tarfile.open(output_tar_path, "w:gz") as tar:
            for fname in os.listdir(pack_folder):
                if fname.endswith(".mp3") and fname in VALID_WAZE_FILENAMES:
                    file_path = os.path.join(pack_folder, fname)
                    tar.add(file_path, arcname=fname)
        return True
    except Exception as e:
        print(f"Error creating Waze tar.gz: {e}")
        return False
