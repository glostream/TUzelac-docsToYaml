# TUzelac-docsToYaml
Fetch Google Docs via API and transform into YAML format

## Setup

1. Install prerequisites with `pip install -r requirements.txt`.
2. The program expects a file `keys/credentials.json` which contains the credentials of the Google app. This can be downloaded from the "APIs & Services > Credentials" tab on the project page in the Google developer console. The file will need to be renamed.
3. A variable called `FOLDER_ID` is declared in `main.py`. This should match with the folder ID on Google drive that contains the documents you wish to process. See below for instructions on how to obtain the folder ID.
4. Run the program with `python3 main.py`.
5. The first time the program is run, it will require authentication. Simply follow the instructions shown. Once completed, a new file `keys/token.json` will be created. No further authentication will be required on subsequent runs.

## How to get folder ID

1. Open Google Drive and right click on the folder.
2. Click "Get Link".
3. Copy the alphanumeric code between `folders/` and `?`.

e.g. for a link

`https://drive.google.com/drive/folders/1ZmrGGtw6E4l6czUb_M1gO9LfaHp3IxJb?usp=sharing`

The ID would be

`1ZmrGGtw6E4l6czUb_M1gO9LfaHp3IxJb`