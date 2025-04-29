# File: __main__.py

import argparse
from steampipe import watcher
from steampipe import processor


def main():
    parser = argparse.ArgumentParser(description="SteamPipe - Steam Clip Uploader")
    parser.add_argument(
        "--clips",
        type=str,
        required=True,
        help="Directory containing Steam clips",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload videos to YouTube",
    )
    parser.add_argument(
        "--privacy",
        default="unlisted",
        choices=["public", "unlisted", "private"],
        help="Privacy setting for uploads",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulates remux/upload without making changes",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Prefix to prepend to the video title",
    )
    parser.add_argument(
        "--discord",
        type=str,
        help="Discord webhook URL for notifications",
    )
    parser.add_argument(
        "--discord-name",
        default="Steampipe",
        help="Override Discord webhook bot name",
    )
    parser.add_argument(
        "--discord-desc",
        default="🔔 New gameplay clip uploaded!",
        help="Override Discord embed description text",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh the Steam app list cache",
    )

    args = parser.parse_args()

    processor.load_steam_apps_cache(force_refresh=args.force_refresh)
    watcher.find_clips(args)


if __name__ == "__main__":
    main()
