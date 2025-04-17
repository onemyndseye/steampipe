import os
import time
import threading
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .processor import (
    get_latest_clip_folder,
    parse_metadata,
    get_game_title,
    remux_clip,
    upload_video
)
from .config import CLIP_DIR


class ClipWatcher(FileSystemEventHandler):
    def __init__(self, args):
        self.args = args

    def on_created(self, event):
        if event.is_directory and os.path.basename(event.src_path).startswith("clip_"):
            print(f"[Watcher] New clip folder detected: {event.src_path}")
            threading.Thread(target=process_clip, args=(event.src_path, self.args)).start()


def wait_for_final_chunks(clip_path, timeout=15, idle_window=2):
    """Wait for session.mpd and confirm .m4s count, size, and first fragment existence."""
    start_time = time.time()
    last_total_size = 0
    last_count = 0
    idle_start = None
    session_path = None

    while time.time() - start_time < timeout:
        found_session = False
        total_size = 0
        chunk_count = 0

        for root, _, files in os.walk(clip_path):
            if "session.mpd" in files:
                found_session = True
                session_path = os.path.join(root, "session.mpd")
            for f in files:
                if f.endswith(".m4s"):
                    chunk_count += 1
                    try:
                        total_size += os.path.getsize(os.path.join(root, f))
                    except FileNotFoundError:
                        continue

        if found_session:
            # Check for first playable fragment
            if session_path and os.path.exists(session_path):
                with open(session_path, "r", encoding="utf-8") as f:
                    mpd_contents = f.read()
                match = re.search(r'chunk-stream0-(\d+)\.m4s', mpd_contents)
                if match:
                    first_chunk = f"chunk-stream0-{match.group(1)}.m4s"
                    chunk_found = any(
                        first_chunk in files
                        for root, _, files in os.walk(clip_path)
                    )
                    if not chunk_found:
                        time.sleep(0.5)
                        continue

            if total_size != last_total_size or chunk_count != last_count:
                last_total_size = total_size
                last_count = chunk_count
                idle_start = time.time()
            elif idle_start and (time.time() - idle_start >= idle_window):
                return True

        time.sleep(0.5)

    return False


def process_clip(clip_path, args):
    if not wait_for_final_chunks(clip_path):
        print(f"⚠️ Clip not ready or timed out: {clip_path}")
        return

    app_id, timestamp = parse_metadata(clip_path)
    game_title = get_game_title(app_id)
    clean_title = game_title.replace("™", "").strip()
    formatted_time = timestamp.replace(":", "-").replace(" ", "_") if timestamp else "unknown"
    out_path = f"/tmp/{clean_title}_{formatted_time}.mp4"

    print(f"🎬 Processing: {clip_path}")
    print(f"▶ Title:      {game_title} – {timestamp}")
    print(f"📼 Output:     {out_path}")

    if remux_clip(clip_path, out_path, dry_run=args.dry_run):
        print("✅ Remux complete.")
        if args.upload:
            upload_video(out_path, game_title, f"Captured on {timestamp}", args.privacy, dry_run=args.dry_run)
    else:
        print("❌ Remux failed.")


def start_watching(args):
    print(f"👀 Watching folder: {CLIP_DIR}")
    event_handler = ClipWatcher(args)
    observer = Observer()
    observer.schedule(event_handler, str(CLIP_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
