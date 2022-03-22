import re
import json
from xml.dom.minidom import Document
import yaml
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
FOLDER_ID = "1gGeoji8R0Empmn1mPFf-nS0pA5Wvoc6F"


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
            flow = InstalledAppFlow.from_client_secrets_file(
                "webcredentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

            # Web flow
            # flow = Flow.from_client_secrets_file(
            #     "webcredentials.json", SCOPES, redirect_uri="http://localhost"
            # )
            # print("Go to this address to authorize the app:", flow.authorization_url())
            # code = input("Enter the authorization code: ")
            # flow.fetch_token(code=code)
            # creds = flow.credentials

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
                q=f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.document'",
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


def parse(document):
    get_text = lambda e: e["paragraph"]["elements"][0]["textRun"]["content"]
    parsed = {"title": document["title"]}
    body = document["body"]

    # transform json document elements into array of lines of text
    lines = []
    for p in body["content"]:
        if "paragraph" in p:
            line = ""
            for e in p["paragraph"]["elements"]:
                line += e["textRun"]["content"]
            lines.append(line)

    # get picture. Text comes after word 'PICTURE: ' and starts after first empty line
    for lix, l in enumerate(lines):
        if "PICTURE:" in l:
            parsed["picture"] = l.split("PICTURE: ")[1]
            continue
        if "picture" in parsed and l == "\n":
            i_pic_end = lix
            break
        if "picture" in parsed:
            parsed["picture"] += l

    i_choices_start = None
    i_choices = []
    for lix, l in enumerate(lines[i_pic_end + 1 :]):
        if not l.split():
            continue
        if len(re.search(r"[A-Z]*", l.split()[0])[0]) > 1:
            # first word is all caps
            if not i_choices_start:
                i_choices_start = lix + i_pic_end + 1
            i_choices.append(lix + i_pic_end + 1)
    i_choices += [lines[i_choices[-1] :].index("\n") + i_choices[-1]]

    # value of 'text' appears between picture and first choice
    parsed["text"] = "".join(lines[i_pic_end + 1 : i_choices_start])

    # choices are marked by all caps
    parsed["choices"] = []
    for ix, i in enumerate(i_choices[:-1]):
        choice = {'text': '', 'days': '', "outcomes": []}
        if 'DAYS' in lines[i]:
            # days may not be specified
            choice["text"] = lines[i].split(" (")[0]
            choice["days"] = int(lines[i].split(" (")[1].replace(" DAYS)", ""))
        else:
            choice['text'] = lines[i]
        for lix, l in enumerate(lines[i : i_choices[ix + 1]]):
            # outcomes begin with a percentage chance followed by single comment
            if re.search(r"\d*%", l.split()[0]):
                outcome = {'text': l, 'comment': lines[i + lix + 1]}
                choice['outcomes'].append(outcome)
        parsed["choices"].append(choice)

    print(json.dumps(parsed, indent=2))
    return parsed


def main():
    creds = authenticate()

    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    items = get_document_ids(drive_service)

    docs_data = get_documents(docs_service, items)

    for d in docs_data:
        parsed = parse(d)
        parsed = json.loads(json.dumps(parsed).replace('\\n', '').replace('\\u000b', ''))
        # print(parsed)
        with open(f"{d['title'].replace(' ', '')}.yml", 'w') as yaml_out:
            yaml.dump(parsed, yaml_out, sort_keys=False)


if __name__ == "__main__":
    main()
