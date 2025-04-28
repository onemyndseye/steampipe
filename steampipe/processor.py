# File: steampipe/processor.py

import os
import json
import re
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path

from .uploader import upload_video

# Define constants
CACHE_FILE = Path(__file__).resolve().parent.parent / "steamappid.json"
CACHE_EXPIRY_DAYS = 7

# Internal cache variable
_steam_apps_cache = {}


def load_steam_apps_cache(force_refresh=False):
    global _steam_apps_cache

    # Check if cache file exists
    if not force_refresh and CACHE_FILE.exists():
        # Check if cache is fresh
        mtime = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime)
        if datetime.now() - mtime < timedelta(days=CACHE_EXPIRY_DAYS):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    _steam_apps_cache = {str(app["appid"]): app["name"] for app in data.get("apps", [])}
                    print(f"[cache] Loaded {_steam_apps_cache.__len__()} apps from cache.")
                    return
            except Exception as e:
                print(f"⚠️ Failed to load cache file: {e}")

    # Refresh cache
    print("[cache] Refreshing Steam app list from API...")
    try:
        response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
        response.raise_for_status()
        apps = response.json().get("applist", {}).get("apps", [])
        _steam_apps_cache = {str(app["appid"]): app["name"] for app in apps}

        # Save to cache
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"apps": apps}, f, indent=2)

        print(f"[cache] Saved {_steam_apps_cache.__len__()} apps to {CACHE_FILE}.")
    except Exception as e:
        print(f"⚠️ Failed to fetch/save Steam app list: {e}")
        _steam_apps_cache = {}


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
    # Lookup app_id in cache
    return _steam_apps_cache.get(str(app_id), "Unknown Game")


def remux_clip(clip_path, output_path, dry_run=False):
    for root, dirs, files in os.walk(clip_path):
        if "session.mpd" in files:
            mpd = os.path.join(root, "session.mpd")
            if dry_run:
                print(f"[DRY RUN] MP4Box -dash 3000 -profile dashavc264:onDemand -out {output_path} {mpd}")
                return True

            try:
                subprocess.run(
                    [
                        "MP4Box",
                        "-dash", "3000",
                        "-profile", "dashavc264:onDemand",
                        "-out", output_path,
                        mpd,
                    ],
                    check=True
                )
                return True
            except subprocess.CalledProcessError as e:
                print(f"[remux] MP4Box failed: {e}")
                return False

    return False


def upload(clip_path, out_path, title, desc, privacy, dry_run=False):
    video_id = upload_video(out_path, title, desc, clip_path=clip_path, privacy=privacy, dry_run=dry_run)
    if video_id:
        return f"https://youtu.be/{video_id}"
    return None
