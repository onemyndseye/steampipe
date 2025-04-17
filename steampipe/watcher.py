import os
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from . import config, processor


class ClipEventHandler(FileSystemEventHandler):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.handled = set()

    def on_created(self, event):
        if event.is_directory and "clip_" in os.path.basename(event.src_path):
            if event.src_path in self.handled:
                return
            self.handled.add(event.src_path)
            threading.Thread(target=self.process_clip, args=(event.src_path,)).start()

    def process_clip(self, clip_path):
        print(f"[Watcher] New clip folder detected: {clip_path}")
        if not processor.wait_for_final_chunks(clip_path):
            print("⏳ Timed out waiting for final chunks.")
            return

        app_id, timestamp = processor.parse_metadata(clip_path)
        if not app_id or not timestamp:
            print("⚠️  Could not parse metadata.")
            return

        title = processor.get_game_title(app_id)
        dt_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        full_title = f"{title} – {dt_str}"
        out_path = f"/tmp/{title.replace('™', '').replace(' ', '_')}_{dt_str.replace(':', '-').replace(' ', '_')}.mp4"

        print(f"▶ Title:      {full_title}")
        print(f"📼 Output:     {out_path}")

        mpd_path = processor.get_clip_mpd(clip_path)
        if not mpd_path:
            print("⚠️  Could not locate .mpd file.")
            return

        if processor.remux_clip(mpd_path, out_path, dry_run=self.args.dry_run):
            print("✅ Remux complete.")
            if self.args.upload:
                success = processor.upload_to_youtube(out_path, full_title, f"Clip recorded on {dt_str}",
                                                      privacy=self.args.privacy, dry_run=self.args.dry_run)
                if success:
                    print("🎉 Upload succeeded.")
        else:
            print("❌ Remux failed.")


def run(args):
    print(f"👀 Watching folder: {config.CLIPS_DIR}")
    event_handler = ClipEventHandler(args)
    observer = Observer()
    observer.schedule(event_handler, config.CLIPS_DIR, recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
