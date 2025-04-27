import re
import shutil
from datetime import datetime
from pathlib import Path

from . import processor
from .discord import send_discord_notification

# Create temp directory at module load
TMP_DIR = Path("/tmp/steampipe")
TMP_DIR.mkdir(parents=True, exist_ok=True)


def is_clip_ready(path):
    timelines = path / "timelines"
    if not timelines.exists() or not timelines.is_dir():
        return False
    if not any(f.suffix == ".json" for f in timelines.iterdir()):
        return False
    return True


def mark_as_processed(path):
    marker = path / ".steampiped"
    with marker.open("w") as f:
        f.write(f"Uploaded on {datetime.now().isoformat()}\n")


def process_clip(clip_path, args):
    print(f"  Processing: {clip_path}")

    app_id, timestamp = processor.parse_metadata(clip_path)
    if not app_id or not timestamp:
        print("❌ Failed to extract metadata.")
        return

    game_title = processor.get_game_title(app_id)
    safe_title = re.sub(r"[^\w\s\-_]", "", game_title)
    safe_timestamp = timestamp.replace(":", "-").replace(" ", "_")

    out_path = TMP_DIR / f"{safe_title}_{safe_timestamp}.mp4"

    full_title = f"{args.prefix}{game_title} – {timestamp}"
    description = f"Automatically captured via Steam background recording.\n\nGame: {game_title}\nTime: {timestamp}"

    print(f"▶️ Title: {full_title}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Output: {out_path}")

    if processor.remux_clip(clip_path, out_path, args.dry_run):
        print("✅ Remux complete.")

        if args.upload:
            print("   Uploading to YouTube...")
            video_url = processor.upload(
                clip_path, out_path, full_title, description, args.privacy, args.dry_run
            )

            if video_url and args.discord and not args.dry_run:
                send_discord_notification(
                    webhook_url=args.discord,
                    title=full_title,
                    video_url=video_url,
                    clip_path=clip_path,
                    username=args.discord_name,
                    description=args.discord_desc
                )
                print(f"[discord] Notification sent for: {full_title}")
            elif not video_url:
                print("❌ Upload failed.")

        mark_as_processed(clip_path)
    else:
        print("❌ Remux failed.")


def find_clips(args):
    clips_dir = Path(args.clips).expanduser().resolve()
    print(f"[finder] Scanning: {clips_dir}")

    found = False

    for sub in sorted(clips_dir.iterdir()):
        if not sub.is_dir():
            continue
        if not sub.name.startswith("clip_"):
            continue
        if (sub / ".steampiped").exists():
            continue

        if not is_clip_ready(sub):
            print(f"[finder] Clip not ready: {sub}")
            continue

        found = True
        process_clip(sub, args)

    if not found:
        print("[finder] No new clips found. Exiting.")

    # Clean up temp directory after all processing
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
        print("[finder] Temp directory cleaned up.")
