# File: __main__.py

import argparse
import logging
from steampipe import reader
from steampipe import processor


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="SteamPipe - Automate uploading your Steam gameplay clips to YouTube.",
        epilog="""
Examples:
  steampipe --clips ~/SteamClips
  steampipe --clips ~/SteamClips --discord https://discord.com/api/webhooks/xxx
  steampipe --clips ~/SteamClips --dry-run

Use --dry-run to simulate remux/upload without making changes.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--clips",
        type=str,
        required=True,
        help="Path to Steam clips folder (required).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate remux/upload without making real changes. [optional]",
    )
    parser.add_argument(
        "--privacy",
        default="unlisted",
        choices=["public", "unlisted", "private"],
        help="Privacy setting for uploaded videos. [optional]",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Prefix to prepend to video titles. [optional]",
    )
    parser.add_argument(
        "--discord",
        type=str,
        help="Discord webhook URL for notifications. [optional]",
    )
    parser.add_argument(
        "--discord-name",
        default="Steampipe",
        help="Override Discord webhook bot name. [optional]",
    )
    parser.add_argument(
        "--discord-desc",
        default="🔔 New gameplay clip uploaded!",
        help="Override Discord embed description text. [optional]",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh the Steam app list cache. [optional]",
    )

    args = parser.parse_args()

    processor.load_steam_apps_cache(force_refresh=args.force_refresh)
    reader.find_clips(args)


if __name__ == "__main__":
    main()
