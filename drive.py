import os.path
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = "1z5qDVpCPszYo3UYTcaK0CJjSh1OFFfIf"

def get_drive_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


service = get_drive_service()


def get_files():
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        pageSize=100,
        fields="files(id,name,mimeType)"
    ).execute()

    return results.get("files", [])

def delete_file(file_id):
    service.files().delete(fileId=file_id).execute()

def download_file(file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)

    return fh


def upload_file(upload_file):
    file_data = upload_file.file.read()

    media = MediaIoBaseUpload(
        io.BytesIO(file_data),
        mimetype=upload_file.content_type,
        resumable=True
    )

    file_metadata = {
        "name": upload_file.filename,
        "parents": [FOLDER_ID]
    }

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

def get_file_name(file_id):
    file = service.files().get(fileId=file_id, fields="name").execute()
    return file.get("name")
