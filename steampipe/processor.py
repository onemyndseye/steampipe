import os
import json
import re
import subprocess
import requests
import time
from datetime import datetime
from .config import CLIP_DIR
from .uploader import upload_video

def get_latest_clip_folder():
    try:
        subdirs = [os.path.join(CLIP_DIR, d) for d in os.listdir(CLIP_DIR)
                   if os.path.isdir(os.path.join(CLIP_DIR, d))]
        return max(subdirs, key=os.path.getmtime) if subdirs else None
    except FileNotFoundError:
        return None

def parse_metadata(clip_path):
    folder_name = os.path.basename(clip_path)
    match = re.match(r"clip_(\d+)_\d+_\d+", folder_name)
    app_id = match.group(1) if match else None

    timeline_path = os.path.join(clip_path, "timelines")
    json_file = next((f for f in os.listdir(timeline_path) if f.endswith(".json")), None)

    if not json_file:
        return app_id, None

    with open(os.path.join(timeline_path, json_file)) as f:
        data = json.load(f)
        timestamp = datetime.fromtimestamp(int(data["daterecorded"]))
        return app_id, timestamp.strftime("%Y-%m-%d %H:%M:%S")

def get_game_title(app_id):
    try:
        response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
        apps = response.json().get("applist", {}).get("apps", [])
        match = next((a for a in apps if str(a.get("appid")) == str(app_id)), None)
        return match["name"] if match else "Unknown Game"
    except Exception as e:
        print(f"⚠️ Failed to fetch game title from Steam API: {e}")
        return "Unknown Game"

def remux_clip(clip_path, output_path, dry_run=False):
    for root, dirs, files in os.walk(clip_path):
        if "session.mpd" in files:
            mpd = os.path.join(root, "session.mpd")
            if dry_run:
                print(f"[DRY RUN] ffmpeg -i {mpd} -c copy {output_path}")
                return True
            subprocess.run(["ffmpeg", "-y", "-i", mpd, "-c", "copy", output_path])
            return True
    return False

def upload(clip_path, out_path, title, desc, privacy, dry_run=False):
    return upload_video(out_path, title, desc, privacy=privacy, dry_run=dry_run)

def wait_for_final_chunks(clip_path, timeout=10, stable_secs=3):
    video_dir = None
    for root, dirs, files in os.walk(clip_path):
        if "session.mpd" in files:
            video_dir = root
            break

    if not video_dir:
        return False

    last_count = -1
    stable_count = 0
    start_time = time.time()

    while time.time() - start_time < timeout:
        m4s_files = [f for f in os.listdir(video_dir) if f.endswith(".m4s")]
        current_count = len(m4s_files)

        if current_count == last_count:
            stable_count += 1
        else:
            stable_count = 0

        if stable_count >= stable_secs:
            return True

        last_count = current_count
        time.sleep(1)

    return False
