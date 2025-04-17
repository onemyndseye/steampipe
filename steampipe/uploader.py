import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from .config import CREDENTIALS_FILE, TOKEN_FILE


def log_error(msg):
    print(f"❌ {msg}")


def upload_video(file_path, title, description, privacy="unlisted", dry_run=False):
    if dry_run:
        print(f"[DRY RUN] Would upload: {file_path}")
        return "https://youtube.com/dummy_video_url"

    try:
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, scopes=["https://www.googleapis.com/auth/youtube.upload"])
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)

        service = build("youtube", "v3", credentials=creds)

        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "20"  # Gaming
            },
            "status": {
                "privacyStatus": privacy
            }
        }

        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

        request = service.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )

        print("🚀 Uploading to YouTube...")
        response = request.execute()

        video_url = f"https://youtube.com/watch?v={response['id']}"
        print(f"🎬 Upload complete: {video_url}")
        print("🎉 Upload succeeded.")
        return video_url

    except HttpError as e:
        log_error(f"YouTube API error: {e}")
        return None
    except Exception as e:
        log_error(f"Upload failed: {e}")
        return None
