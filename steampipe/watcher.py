import os
import time
import re
from threading import Thread
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from . import processor
from .config import CLIP_DIR

clip_queue = Queue()

def wait_for_path(path, timeout=6, check_file=None):
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(path):
            if check_file:
                try:
                    if any(f.endswith(check_file) for f in os.listdir(path)):
                        return True
                except FileNotFoundError:
                    pass
            else:
                return True
        time.sleep(0.2)
    return False

def process_clip(clip_path, args):
    print(f"🎬 Processing: {clip_path}")

    timeline_dir = os.path.join(clip_path, "timelines")
    if not wait_for_path(timeline_dir, timeout=6, check_file=".json"):
        print(f"❌ Timelines directory or .json not ready: {timeline_dir}")
        return

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

    print(f"▶️ Title:      {full_title}")
    print(f"🕒 Timestamp:  {timestamp}")
    print(f"📼 Output:     {out_path}")

    if not processor.wait_for_final_chunks(clip_path):
        print("⚠️ Clip chunks did not stabilize in time. Skipping.")
        return

    if processor.remux_clip(clip_path, out_path, args.dry_run):
        print("✅ Remux complete.")
        if args.upload:
            print("🚀 Uploading to YouTube...")
            if processor.upload(clip_path, out_path, full_title, description, args.privacy, args.dry_run):
                print("🎉 Upload succeeded.")
            else:
                print("❌ Upload failed.")
    else:
        print("❌ Remux failed.")

def worker(args):
    while True:
        clip_path = clip_queue.get()
        if clip_path is None:
            break
        process_clip(clip_path, args)
        clip_queue.task_done()

class ClipEventHandler(FileSystemEventHandler):
    def __init__(self, args):
        self.args = args

    def on_created(self, event):
        if event.is_directory and os.path.basename(event.src_path).startswith("clip_"):
            print(f"[Watcher] New clip folder detected: {event.src_path}")
            clip_queue.put(event.src_path)

def watch_clips(args):
    print(f"👀 Watching folder: {CLIP_DIR}")
    observer = Observer()
    handler = ClipEventHandler(args)
    observer.schedule(handler, CLIP_DIR, recursive=False)

    thread = Thread(target=worker, args=(args,), daemon=True)
    thread.start()

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Watcher stopped.")
        observer.stop()
        clip_queue.put(None)
    observer.join()
    thread.join()
