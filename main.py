from src import api
from src import parser
import yaml, os

from googleapiclient.discovery import build

KEYS = {"token": "keys/token.json", "credentials": "keys/credentials.json"}
# ID of the folder on Google drive containing the documents
FOLDER_ID = "1G1kgyyXNRQucc6zyh6rIV_0LfX-HwDV5"  # Events
OUTPUT_PATH = "out/"


def parse_documents(docs_data):
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)

    for d in docs_data[::-1]:
        print(d["title"])
        try:
            parsed = parser.parse(d)
        except:
            print("ERROR: could not parse document")
            continue
        if not parsed:
            continue
        path = f"{OUTPUT_PATH}/{d['title'].replace(' ', '')}.yml"
        with open(path, "w") as yaml_out:
            yaml.dump(parsed, yaml_out, sort_keys=False)


def main():
    creds = api.authenticate(KEYS)
    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    print("Getting document metadata...")
    items = api.get_document_ids(drive_service, FOLDER_ID)

    print("\nReading documents...")
    docs_data = api.read_documents(docs_service, items)

    print("\nParsing...")
    parse_documents(docs_data)

    print("\nComplete!")


if __name__ == "__main__":
    main()
