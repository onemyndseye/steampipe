# steampipe/__main__.py

import argparse
from steampipe import watcher

def main():
    parser = argparse.ArgumentParser(description="SteamPipe - Steam Clip Watcher and Uploader")
    parser.add_argument("--watch", type=str, required=True, help="Directory to monitor for new clips")
    parser.add_argument("--upload", action="store_true", help="Upload videos to YouTube")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"], help="Privacy setting for uploads")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without making changes")
    parser.add_argument("--prefix", default="", help="Prefix to prepend to the video title")

    args = parser.parse_args()
    watcher.watch_clips(args)

if __name__ == "__main__":
    main()
