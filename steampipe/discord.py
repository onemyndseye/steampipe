# steampipe/discord.py

import requests

AVATAR_URL = "https://raw.githubusercontent.com/onemyndseye/steampipe/main/steampipe/assets/steampipe-icon.png"

def send_discord_notification(webhook_url, title, video_url):
    data = {
        "content": video_url,
        "avatar_url": AVATAR_URL
    }

    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            print(f"[discord] Warning: non-204 response: {response.status_code}")
    except Exception as e:
        print(f"[discord] Error sending notification: {e}")
