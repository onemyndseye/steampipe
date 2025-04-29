# File: reader.py

import re
import shutil
import logging
from datetime import datetime
from pathlib import Path

from . import processor
from .discord import send_discord_notification

logger = logging.getLogger(__name__)

TMP_DIR = Path("/tmp/steampipe")
TMP_DIR.mkdir(parents=True, exist_ok=True)


def is_clip_ready(path):
    timelines = path / "timelines"
    return timelines.exists() and timelines.is_dir() and any(f.suffix == ".json" for f in timelines.iterdir())


def mark_as_processed(path):
    marker = path / ".steampiped"
    with marker.open("w") as f:
        f.write(f"Uploaded on {datetime.now().isoformat()}\n")


def process_clip(clip_path, args):
    logger.info(f"Processing: {clip_path}")

    app_id, timestamp = processor.parse_metadata(clip_path)
    if not app_id or not timestamp:
        logger.error("❌ Failed to extract metadata.")
        return

    game_title = processor.get_game_title(app_id)
    safe_title = re.sub(r"[^\w\s\-_]", "", game_title)
    safe_timestamp = timestamp.replace(":", "-").replace(" ", "_")

    out_path = TMP_DIR / f"{safe_title}_{safe_timestamp}.mp4"

    full_title = f"{args.prefix}{game_title} – {timestamp}"
    description = f"Automatically captured via Steam background recording.\n\nGame: {game_title}\nTime: {timestamp}"

    logger.info(f"▶️ Title: {full_title}")
    logger.info(f"   Timestamp: {timestamp}")
    logger.info(f"   Output: {out_path}")

    if processor.remux_clip(clip_path, out_path, args.dry_run):
        logger.info("✅ Remux complete.")

        if not args.dry_run:
            logger.info("   Uploading to YouTube...")
            video_url = processor.upload(
                clip_path, out_path, full_title, description, args.privacy, args.dry_run
            )

            if video_url and args.discord:
                send_discord_notification(
                    webhook_url=args.discord,
                    title=full_title,
                    video_url=video_url,
                    clip_path=clip_path,
                    username=args.discord_name,
                    description=args.discord_desc
                )
                logger.info(f"[discord] Notification sent for: {full_title}")
            elif not video_url:
                logger.error("❌ Upload failed.")

        mark_as_processed(clip_path)
    else:
        logger.error("❌ Remux failed.")


def find_clips(args):
    clips_dir = Path(args.clips).expanduser().resolve()
    logger.info(f"[finder] Scanning: {clips_dir}")

    found = False

    for sub in sorted(clips_dir.iterdir()):
        if not sub.is_dir() or not sub.name.startswith("clip_"):
            continue
        if (sub / ".steampiped").exists():
            continue
        if not is_clip_ready(sub):
            logger.warning(f"[finder] Clip not ready: {sub}")
            continue

        found = True
        process_clip(sub, args)

    if not found:
        logger.info("[finder] No new clips found. Exiting.")

    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
        logger.info("[finder] Temp directory cleaned up.")
