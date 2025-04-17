import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def upload_video(file_path, title, description, privacy="unlisted"):
    creds_path = os.path.expanduser("~/.config/steampipe/credentials.json")
    creds = Credentials.from_authorized_user_file(creds_path)

    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": privacy
            }
        },
        media_body=MediaFileUpload(file_path)
    )
    response = request.execute()
    return f"https://youtube.com/watch?v={response['id']}"
