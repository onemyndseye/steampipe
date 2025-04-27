import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "credentials", "credentials.json"))
TOKEN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "credentials", "token.pickle"))


def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)


def upload_video(filepath, title, description, clip_path, privacy="unlisted", dry_run=False):
    if dry_run:
        print(f"[DRY RUN] Would upload '{filepath}' with title: '{title}' and privacy: '{privacy}'")
        return "DRY_RUN_FAKE_ID"

    service = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [],
            "categoryId": "20",
        },
        "status": {
            "privacyStatus": privacy,
        }
    }

    media = MediaFileUpload(filepath, chunksize=-1, resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"🎬 Upload complete: https://youtube.com/watch?v={video_id}")

    # Set thumbnail after upload
    thumbnail_path = os.path.join(clip_path, "thumbnail.jpg")
    if os.path.exists(thumbnail_path):
        set_thumbnail(video_id, thumbnail_path)
    else:
        print(f"No thumbnail.jpg found in clip folder {clip_path}, skipping thumbnail upload.")

    return video_id


def set_thumbnail(video_id, thumbnail_path):
    service = get_authenticated_service()

    media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
    request = service.thumbnails().set(
        videoId=video_id,
        media_body=media
    )
    response = request.execute()
    print(f"🖼️ Thumbnail uploaded for video {video_id}")
    return response
