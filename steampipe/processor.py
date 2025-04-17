import os
import json
import re
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from .config import CLIP_DIR, get_config_path
from .uploader import upload_video


def log_error(msg):
    print(f"❌ {msg}")


# -------------------------------
# 📼 Clip Scanning + Metadata
# -------------------------------

def get_latest_clip_folder():
    try:
        subdirs = [os.path.join(CLIP_DIR, d) for d in os.listdir(CLIP_DIR)
                   if os.path.isdir(os.path.join(CLIP_DIR, d))]
        return max(subdirs, key=os.path.getmtime) if subdirs else None
    except Exception as e:
        log_error(f"Could not read clip directory: {e}")
        return None


def parse_metadata(clip_path):
    folder_name = os.path.basename(clip_path)
    match = re.match(r"clip_(\d+)_\d+_\d+", folder_name)
    app_id = match.group(1) if match else None

    timeline_path = os.path.join(clip_path, "timelines")
    try:
        json_file = next((f for f in os.listdir(timeline_path) if f.endswith(".json")), None)
        if not json_file:
            log_error(f"No JSON metadata found in: {timeline_path}")
            return app_id, None
        with open(os.path.join(timeline_path, json_file)) as f:
            data = json.load(f)
            timestamp = datetime.fromtimestamp(int(data["daterecorded"]))
            return app_id, timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        log_error(f"Error parsing metadata: {e}")
        return app_id, None


# -------------------------------
# 🎮 Game Title Lookup + Caching
# -------------------------------

APP_CACHE_FILE = get_config_path("applist_cache.json")
APP_CACHE_TTL = 86400  # 24 hours


def load_app_cache():
    if not APP_CACHE_FILE.exists():
        return {}

    try:
        with open(APP_CACHE_FILE, "r") as f:
            data = json.load(f)
            if time.time() - data.get("timestamp", 0) > APP_CACHE_TTL:
                return {}
            return data.get("apps", {})
    except Exception as e:
        log_error(f"Failed to load app cache: {e}")
        return {}


def save_app_cache(apps):
    try:
        with open(APP_CACHE_FILE, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "apps": apps
            }, f)
    except Exception as e:
        log_error(f"Failed to save app cache: {e}")


def fetch_steam_apps():
    try:
        response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
        apps = response.json().get("applist", {}).get("apps", [])
        return {str(app["appid"]): app["name"] for app in apps}
    except Exception as e:
        log_error(f"Steam API fetch failed: {e}")
        return {}


def get_game_title(app_id):
    cache = load_app_cache()

    if str(app_id) in cache:
        return cache[str(app_id)]

    apps = fetch_steam_apps()
    if not apps:
        return "Unknown Game"

    save_app_cache(apps)
    return apps.get(str(app_id), "Unknown Game")


# -------------------------------
# 🎬 Remuxing + Export
# -------------------------------

def remux_clip(clip_path, output_path, dry_run=False):
    for root, dirs, files in os.walk(clip_path):
        if "session.mpd" in files:
            mpd = os.path.join(root, "session.mpd")
            try:
                if dry_run:
                    print(f"[DRY RUN] ffmpeg -i {mpd} -c copy {output_path}")
                    return True
                subprocess.run(["ffmpeg", "-y", "-i", mpd, "-c", "copy", output_path], check=True)
                return True
            except subprocess.CalledProcessError as e:
                log_error(f"ffmpeg remux failed: {e}")
                return False
    log_error("No session.mpd file found for remuxing.")
    return False
