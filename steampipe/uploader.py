import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = os.path.expanduser("~/.config/steampipe/credentials.json")
TOKEN_FILE = os.path.expanduser("~/.config/steampipe/token.pickle")

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

def upload_video(filepath, title, description, privacy="unlisted", dry_run=False):
    if dry_run:
        print(f"[DRY RUN] Would upload '{filepath}' with title: '{title}' and privacy: '{privacy}'")
        return True

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

    print(f"🎬 Upload complete: https://youtube.com/watch?v={response['id']}")
    return True
