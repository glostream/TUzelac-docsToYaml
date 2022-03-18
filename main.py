import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]
FOLDER_ID = "1ZmrGGtw6E4l6czUb_M1gO9LfaHp3IxJb"


def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Local desktop flow
            # flow = InstalledAppFlow.from_client_secrets_file("webcredentials.json", SCOPES)
            # creds = flow.run_local_server(port=0)
            
            # Web flow
            flow = Flow.from_client_secrets_file(
                "webcredentials.json", SCOPES, redirect_uri="http://localhost"
            )
            print("Go to this address to authorize the app:", flow.authorization_url())
            code = input("Enter the authorization code: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_document_ids(drive):
    try:
        # Search for all files in specific folder with id
        results = (
            drive.files()
            .list(
                q=f"'{FOLDER_ID}' in parents",
                fields="nextPageToken, files(id, name)",
                pageSize=10,
            )
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return
        print("Files:")
        for item in items:
            print("{0} ({1})".format(item["name"], item["id"]))
    except HttpError as error:
        print(f"An error occurred: {error}")

    return items


def get_documents(docs, items):
    try:
        for item in items:
            document = docs.documents().get(documentId=item["id"]).execute()
            print(document.get("body"))
    except HttpError as error:
        print(f"An error occurred: {error}")


def main():
    creds = authenticate()

    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    items = get_document_ids(drive_service)

    # get_documents(docs_service, items)


if __name__ == "__main__":
    main()
