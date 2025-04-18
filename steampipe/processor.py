# steampipe/processor.py

import os
import re
import json
import time
import shutil
import subprocess
from datetime import datetime

from .uploader import upload_video
from .appid_cache import get_title


def parse_metadata(clip_dir):
    timeline_path = os.path.join(clip_dir, "video")
    json_file = next((f for f in os.listdir(timeline_path) if f.endswith(".json")), None)
    if not json_file:
        raise FileNotFoundError("No timeline JSON found in video/")

    json_path = os.path.join(timeline_path, json_file)
    with open(json_path, "r") as f:
        data = json.load(f)

    app_id = str(data.get("AppID", "Unknown"))
    timestamp_unix = data.get("Timestamp", 0)
    timestamp = datetime.fromtimestamp(timestamp_unix)
    return app_id, timestamp


def get_latest_clip_folder(clips_dir):
    folders = [
        os.path.join(clips_dir, d)
        for d in os.listdir(clips_dir)
        if os.path.isdir(os.path.join(clips_dir, d))
    ]
    if not folders:
        return None
    return max(folders, key=os.path.getmtime)


def wait_for_final_chunks(clip_dir, timeout=30):
    video_dir = os.path.join(clip_dir, "video")
    session_file = None

    for _ in range(timeout):
        session_files = [
            f for f in os.listdir(video_dir)
            if f.startswith("bg_") and os.path.isdir(os.path.join(video_dir, f))
        ]
        if not session_files:
            time.sleep(1)
            continue

        session_path = os.path.join(video_dir, session_files[0])
        manifest_path = os.path.join(session_path, "session.mpd")
        if os.path.exists(manifest_path):
            session_file = manifest_path
            break
        time.sleep(1)

    if not session_file:
        print("❌ session.mpd not found.")
    return session_file


def remux_clip(clip_dir, output_path):
    manifest = wait_for_final_chunks(clip_dir)
    if not manifest:
        return False

    try:
        subprocess.run(
            ["ffmpeg", "-i", manifest, "-c", "copy", output_path],
            check=True
        )
        print("✅ Remux complete.")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Remux failed:\nffmpeg -i {manifest} -c copy {output_path}")
        return False


def upload(clip_dir, output_path, title, description, privacy, dry_run):
    if dry_run:
        print(f"[DRY RUN] Would run: ffmpeg -i {clip_dir} -c copy {output_path}")
        print("\n✅ Export complete:")
        print(f"▶  Title:      {title}")
        print(f"🕒  Timestamp:  {description}")
        print(f"📼  Output:     {output_path}")
        print("🧪 Dry run mode active — no files were written.")
        return True

    print("🚀 Uploading to YouTube...")
    try:
        video_url = upload_video(output_path, title, description, privacy)
        print(f"🎬 Upload complete: {video_url}")
        print("🎉 Upload succeeded.")
        return True
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
        return False


def resolve_app_title(app_id):
    # fallback resolution, this could be an actual Steam API call
    return f"Unknown Game (AppID {app_id})"


def get_clip_title(app_id, timestamp):
    title = get_title(app_id, resolve_app_title)
    return f"{title} – {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
