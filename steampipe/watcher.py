# steampipe/watcher.py

import os
import time
import re
from datetime import datetime
from pathlib import Path

from . import processor

def is_clip_ready(path):
    timelines = path / "timelines"
    if not timelines.exists() or not timelines.is_dir():
        return False
    if not any(f.suffix == ".json" for f in timelines.iterdir()):
        return False
    return True

def mark_as_processed(path):
    marker = path / ".steampiped"
    with marker.open("w") as f:
        f.write(f"Uploaded on {datetime.now().isoformat()}\n")

def process_clip(clip_path, args):
    print(f"  Processing: {clip_path}")

    app_id, timestamp = processor.parse_metadata(clip_path)
    if not app_id or not timestamp:
        print("❌ Failed to extract metadata.")
        return

    game_title = processor.get_game_title(app_id)
    safe_title = re.sub(r"[^\w\s\-_]", "", game_title)
    safe_timestamp = timestamp.replace(":", "-").replace(" ", "_")
    out_path = f"/tmp/{safe_title}_{safe_timestamp}.mp4"

    full_title = f"{args.prefix}{game_title} – {timestamp}"
    description = f"Automatically captured via Steam background recording.\n\nGame: {game_title}\nTime: {timestamp}"

    print(f"▶️ Title: {full_title}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Output: {out_path}")

    if not processor.wait_for_final_chunks(clip_path):
        print("⚠️ Clip chunks did not stabilize in time. Skipping.")
        return

    if processor.remux_clip(clip_path, out_path, args.dry_run):
        print("✅ Remux complete.")

        if args.upload:
            print("   Uploading to YouTube...")
            if processor.upload(clip_path, out_path, full_title, description, args.privacy, args.dry_run):
                print("   Upload succeeded.")
            else:
                print("❌ Upload failed.")
    else:
        print("❌ Remux failed.")

def watch_clips(args):
    clips_dir = Path(args.watch).expanduser().resolve()
    print(f"[watcher] Scanning: {clips_dir}")
    print(f"[watcher] Every {args.sync_delay}s | Process delay: {args.proc_delay}s")

    while True:
        for sub in sorted(clips_dir.iterdir()):
            if not sub.is_dir():
                continue
            if not sub.name.startswith("clip_"):
                continue
            if (sub / ".steampiped").exists():
                continue

            print(f"[watcher] Found new clip: {sub}")
            time.sleep(args.proc_delay)

            if not is_clip_ready(sub):
                print(f"[watcher] Clip not ready: {sub}")
                continue

            process_clip(sub, args)
            mark_as_processed(sub)

        time.sleep(args.sync_delay)
