# steampipe/discord.py

import requests

def send_discord_notification(webhook_url, title, video_url):
    data = {
        "embeds": [
            {
                "title": "🎬 Clip Uploaded",
                "description": f"**{title}**\n[📺 Watch on YouTube]({video_url})",
                "color": 0x1abc9c,
                "footer": {"text": "SteamPipe"},
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            print(f"[discord] Warning: non-204 response: {response.status_code}")
    except Exception as e:
        print(f"[discord] Error sending notification: {e}")
