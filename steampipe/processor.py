import os
import json
import time
import subprocess
from datetime import datetime
from .uploader import upload_video
from . import config


def parse_metadata(clip_path):
    timeline_path = os.path.join(clip_path, "timelines")
    if not os.path.exists(timeline_path):
        return None, None
    json_file = next((f for f in os.listdir(timeline_path) if f.endswith(".json")), None)
    if not json_file:
        return None, None
    with open(os.path.join(timeline_path, json_file)) as f:
        data = json.load(f)
        app_id = clip_path.split("_")[1]
        timestamp = int(data.get("daterecorded", 0))
        return app_id, timestamp


def get_game_title(app_id):
    game_map = {
        "553850": "HELLDIVERS™ 2"
    }
    return game_map.get(app_id, "Unknown Game")


def get_clip_mpd(clip_path):
    video_path = os.path.join(clip_path, "video")
    for root, _, files in os.walk(video_path):
        for file in files:
            if file.endswith(".mpd"):
                return os.path.join(root, file)
    return None


def wait_for_final_chunks(clip_path, timeout=10, interval=1):
    start_time = time.time()
    while time.time() - start_time < timeout:
        mpd_path = get_clip_mpd(clip_path)
        if mpd_path and os.path.exists(mpd_path):
            return True
        time.sleep(interval)
    return False


def remux_clip(mpd_path, output_path, dry_run=False):
    cmd = ["ffmpeg", "-i", mpd_path, "-c", "copy", output_path]
    if dry_run:
        print(f"[DRY RUN] Would run: {' '.join(cmd)}")
        return True
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def upload_to_youtube(output_path, title, description, privacy, dry_run=False):
    if dry_run:
        print(f"[DRY RUN] Would upload {output_path} to YouTube with title '{title}'")
        return True
    try:
        url = upload_video(output_path, title=title, description=description, privacy=privacy)
        print(f"🎬 Upload complete: {url}")
        return True
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
        return False
