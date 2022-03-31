import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError


def authenticate(keys):
    # If modifying these scopes, delete the file token.json.
    scopes = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/documents.readonly",
    ]
    key, credentials = keys.values()
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(key):
        creds = Credentials.from_authorized_user_file(key, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(key, "w") as token:
            token.write(creds.to_json())
    return creds


def get_document_ids(drive, folder):
    try:
        # Search for all files in specific folder with id
        results = (
            drive.files()
            .list(
                # only get files of google doc type that are inside folder with FOLDER_ID
                q=f"'{folder}' in parents and mimeType='application/vnd.google-apps.document'",
                pageSize=1000,
            )
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return
        for item in items:
            print("{0} ({1})".format(item["name"], item["id"]))
    except HttpError as e:
        print(f"An error occurred: {e}")
    return items


def read_documents(docs, items):
    doc_data = []
    try:
        for item in items:
            document = docs.documents().get(documentId=item["id"]).execute()
            doc_data.append(document)
    except HttpError as e:
        print(f"An error occurred: {e}")
    return doc_data
