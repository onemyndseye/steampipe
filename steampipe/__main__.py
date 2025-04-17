import argparse
import sys

from . import watcher, processor, config


def main():
    print("Steampipe starting...")

    parser = argparse.ArgumentParser(description="Steampipe: Upload Steam clips to YouTube.")
    parser.add_argument("--watch", action="store_true", help="Watch for new clips")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube after processing")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"],
                        help="YouTube video privacy setting")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the process without making changes")
    args = parser.parse_args()

    if args.watch:
        watcher.run(args)
    else:
        print("Use --watch to start monitoring clip folder.")


# Ensure main() runs when invoked as: python3 -m steampipe
main()
