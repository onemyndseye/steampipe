import os
import time
import threading
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from . import processor
from .config import Config


class ClipHandler(FileSystemEventHandler):
    def __init__(self, args):
        self.args = args
        super().__init__()

    def on_created(self, event):
        if event.is_directory and "clip_" in event.src_path:
            print(f"[Watcher] New clip folder detected: {event.src_path}")
            threading.Thread(
                target=self.worker_thread, args=(event.src_path,)
            ).start()

    def worker_thread(self, clip_path):
        print(f"🎬 Processing: {clip_path}")
        app_id, timestamp = processor.parse_metadata(clip_path)
        if not app_id or not timestamp:
            print("⚠️  Failed to parse metadata.")
            return

        title = processor.lookup_game_title(app_id)
        ts = datetime.datetime.fromtimestamp(timestamp)
        full_title = f"{title} – {ts.strftime('%Y-%m-%d %H:%M:%S')}"
        safe_title = title.replace('™', '').replace(' ', '_')
        output = f"/tmp/{safe_title}_{ts.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"

        print(f"▶ Title:      {full_title}")
        print(f"📼 Output:     {output}")

        if not processor.wait_for_final_chunks(clip_path):
            print("⏳ Clip not ready — skipping.")
            return

        try:
            video_dir = os.path.join(clip_path, "video")
            subfolder = next(
                d for d in os.listdir(video_dir) if d.startswith("bg_")
            )
            session_mpd = os.path.join(video_dir, subfolder, "session.mpd")
            processor.remux_clip(session_mpd, output)
            print("✅ Remux complete.")

            if self.args.upload:
                print("🚀 Uploading to YouTube...")
                success = processor.upload_and_log(
                    output,
                    full_title,
                    ts.strftime("Recorded on %B %d, %Y"),
                    self.args.privacy,
                    self.args.dry_run,
                )
                if success:
                    print("🎉 Upload succeeded.")
                else:
                    print("❌ Upload failed.")

        except Exception as e:
            print(f"❌ Processing error: {e}")


def run(args):
    clips_dir = os.path.expanduser(Config.CLIPS_DIR)
    print(f"👀 Watching folder: {clips_dir}")
    event_handler = ClipHandler(args)
    observer = Observer()
    observer.schedule(event_handler, clips_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
