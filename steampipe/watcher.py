# steampipe/watcher.py

import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from . import processor


class ClipHandler(FileSystemEventHandler):
    def __init__(self, args):
        self.args = args
        self.active_threads = {}

    def on_created(self, event):
        if not event.is_directory:
            return

        full_path = event.src_path
        if "clip_" not in os.path.basename(full_path):
            return

        print(f"[Watcher] New clip folder detected: {full_path}")

        if full_path in self.active_threads:
            return

        t = threading.Thread(target=self.worker, args=(full_path,))
        t.start()
        self.active_threads[full_path] = t

    def worker(self, clip_path):
        print(f"🎬 Processing: {clip_path}")
        processor.process_clip(
            clip_path=clip_path,
            upload=self.args.upload,
            privacy=self.args.privacy,
            dry_run=self.args.dry_run
        )
        self.active_threads.pop(clip_path, None)


def run(args):
    clips_dir = os.path.expanduser(args.watch)
    if not os.path.isdir(clips_dir):
        print(f"❌ Error: {clips_dir} is not a valid directory.")
        return

    print(f"👀 Watching folder: {clips_dir}")

    event_handler = ClipHandler(args)
    observer = Observer()
    observer.schedule(event_handler, path=clips_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
