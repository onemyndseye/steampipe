# steampipe/discord.py

import requests
import os
import json

AVATAR_URL = "https://raw.githubusercontent.com/onemyndseye/steampipe/main/steampipe/assets/steampipe-icon.png"


def send_discord_notification(webhook_url, title, video_url, clip_path):
    thumbnail_path = os.path.join(clip_path, "thumbnail.jpg")
    files = None
    data = None

    payload = {
        "username": "SteamPipe",
        "avatar_url": AVATAR_URL,
        "embeds": [
            {
                "title": f"▶️ {title}",
                "url": video_url,
                "description": "🔔 New gameplay clip uploaded!\n\nCheck it out now.",
                "color": 0x00FFFF,
                "image": {},
                "footer": {
                    "text": "Auto-uploaded via SteamPipe"
                }
            }
        ]
    }

    if os.path.exists(thumbnail_path):
        files = {"file": open(thumbnail_path, "rb")}
        payload["embeds"][0]["image"]["url"] = "attachment://thumbnail.jpg"

    data = {"payload_json": json.dumps(payload)}

    try:
        response = requests.post(webhook_url, data=data, files=files)
        if files:
            files["file"].close()
        if response.status_code not in (200, 204):
            print(f"[discord] Warning: non-2xx response: {response.status_code} | {response.text}")
    except Exception as e:
        print(f"[discord] Error sending notification: {e}")
