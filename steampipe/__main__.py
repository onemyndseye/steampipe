import argparse

from steampipe import watcher


def main():
    print("Steampipe starting...")

    parser = argparse.ArgumentParser(
        description="Steampipe: Upload Steam clips to YouTube."
    )
    parser.add_argument(
        "--watch",
        metavar="DIR",
        help="Watch the given directory for new clips",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload to YouTube after processing",
    )
    parser.add_argument(
        "--privacy",
        default="unlisted",
        choices=["public", "unlisted", "private"],
        help="YouTube video privacy setting",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the process without making changes",
    )

    args = parser.parse_args()

    if args.watch:
        watcher.run(args)
    else:
        print("Use --watch DIR to start monitoring a clip folder.")


if __name__ == "__main__":
    main()
