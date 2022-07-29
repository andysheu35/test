from __future__ import print_function
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "key.json"


credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# If modifying these scopes, delete the file token.json.


# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1wqQG0yuyiCtkvYw4pIqu-r4iN_BF---wTvlQ69oBBOo"


try:
    service = build("sheets", "v4", credentials=credentials)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="in!A1:H24")
        .execute()
    )
    values = result.get("values", [])
    aoa = [[4, 3], [5, 6], [6, 7]]
    number = 2
    request = (
        sheet.values()
        .update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=f"sheet!A{number}",
            valueInputOption="USER_ENTERED",
            body={"values": aoa},
        )
        .execute()
    )

    print(values)
except HttpError as err:
    print(err)
