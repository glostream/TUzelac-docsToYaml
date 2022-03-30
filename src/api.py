import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from googleapiclient.errors import HttpError


def authenticate(scopes):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("keys/token.json"):
        creds = Credentials.from_authorized_user_file("keys/token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Local desktop flow
            flow = InstalledAppFlow.from_client_secrets_file("keys/janko.json", scopes)
            creds = flow.run_local_server(port=0)

            # Web flow
            # flow = Flow.from_client_secrets_file(
            #     "webcredentials.json", scopes, redirect_uri="http://localhost"
            # )
            # print("Go to this address to authorize the app:", flow.authorization_url())
            # code = input("Enter the authorization code: ")
            # flow.fetch_token(code=code)
            # creds = flow.credentials

        # Save the credentials for the next run
        with open("keys/token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_document_ids(drive, folder):
    try:
        # Search for all files in specific folder with id
        results = (
            drive.files()
            .list(
                # only get files of google doc type
                q=f"'{folder}' in parents and mimeType='application/vnd.google-apps.document'",
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
    doc_data = []
    try:
        for item in items:
            document = docs.documents().get(documentId=item["id"]).execute()
            doc_data.append(document)
    except HttpError as error:
        print(f"An error occurred: {error}")
    return doc_data
