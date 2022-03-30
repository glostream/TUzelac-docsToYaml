from src import api
from src import parser
import yaml

from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]
# FOLDER_ID = "1zCCZxTIyigqkixHQtt4euLyfAC_p9Hyb" # test 1
FOLDER_ID = "1G1kgyyXNRQucc6zyh6rIV_0LfX-HwDV5"  # test 2


def main():
    print("Authenticating...")
    creds = api.authenticate(SCOPES)

    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    print("\nGetting document metadata...")
    items = api.get_document_ids(drive_service, FOLDER_ID)

    print("\nReading documents...")
    docs_data = api.get_documents(docs_service, items)

    print("\nParsing...")
    for d in docs_data[::-1]:
        # if d["title"] != "The Umbrella Man":  # document is temporarily bugged
        #     continue
        print(d["title"])
        parsed = parser.parse(d)
        if not parsed:
            continue
        out_path = f"out/{d['title'].replace(' ', '')}.yml"
        with open(out_path, "w") as yaml_out:
            yaml.dump(parsed, yaml_out, sort_keys=False)
        # break

    print("\nComplete!")


if __name__ == "__main__":
    main()
