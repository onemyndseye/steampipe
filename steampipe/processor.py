import os
import json
import subprocess
import time
from datetime import datetime

from .config import Config
from .uploader import upload_video


def parse_metadata(clip_path):
    timeline_path = os.path.join(clip_path, "video")
    json_file = next(
        (f for f in os.listdir(timeline_path) if f.endswith(".json")),
        None
    )
    if not json_file:
        raise FileNotFoundError("Timeline metadata JSON not found.")

    json_path = os.path.join(timeline_path, json_file)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    app_id = data.get("AppID", "unknown")
    time_seconds = int(data.get("StartTime", 0))
    timestamp = datetime.fromtimestamp(time_seconds)
    return app_id, timestamp


def get_game_title(app_id):
    titles_db = Config.APP_ID_DB
    return titles_db.get(str(app_id), "Unknown Game")


def build_output_path(title, timestamp):
    safe_title = title.replace("™", "").replace(":", "").replace("/", "-")
    filename = f"{safe_title}_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
    return os.path.join("/tmp", filename)


def remux_clip(clip_path, output_path, dry_run=False):
    session_path = os.path.join(
        clip_path, "video", os.listdir(os.path.join(clip_path, "video"))[0],
        "session.mpd"
    )

    cmd = [
        "ffmpeg", "-i", session_path,
        "-c", "copy", output_path
    ]

    if dry_run:
        print("[DRY RUN] Would run:", " ".join(cmd))
        return True

    try:
        subprocess.run(cmd, check=True)
        print("✅ Remux complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Remux failed:\n{e}")
        return False

    return True


def upload_to_youtube(filepath, title, description, privacy, dry_run=False):
    if dry_run:
        print("[DRY RUN] Would upload to YouTube:", filepath)
        return True

    try:
        video_url = upload_video(filepath, title, description, privacy)
        print("🎬 Upload complete:", video_url)
        return True
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
        return False


def wait_for_final_chunks(clip_path, timeout=15):
    video_path = os.path.join(clip_path, "video")
    for _ in range(timeout):
        if os.path.isdir(video_path) and any(
            "session.mpd" in f for f in os.listdir(video_path)
        ):
            return True
        time.sleep(1)
    return False
