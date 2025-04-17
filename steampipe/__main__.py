import argparse
from . import watcher, processor

def main():
    parser = argparse.ArgumentParser(description="Steampipe: Upload Steam clips to YouTube")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions only")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube")
    parser.add_argument("--privacy", default="unlisted", help="YouTube video privacy")
    parser.add_argument("--prefix", default="", help="Prefix for the video title")
    parser.add_argument("--watch", action="store_true", help="Watch folder for new clips")
    args = parser.parse_args()

    if args.watch:
        watcher.watch_clips(args)
    else:
        clip_path = processor.get_latest_clip_folder()
        if clip_path:
            watcher.process_clip(clip_path, args)
        else:
            print("No clip folders found.")

if __name__ == "__main__":
    main()
