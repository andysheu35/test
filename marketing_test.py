from os import error
import requests
import json
from time import sleep
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


def get_api_tukey(headers, payload, mode):
    post_response = requests.post(
        "https://" + mode + ".chimes.ai/tukey/tukey/api/",
        data=json.dumps(payload),
        headers=headers,
    )
    post_result = post_response.json()
    result_api = post_result["id"]
    print(post_result)
    return result_api


def get_response_tukey(result_api, mode):
    url = "https://" + mode + ".chimes.ai/tukey/tukey/api/" + result_api + "/"
    calculation = requests.get(url)
    calculation_result = calculation.json()
    answer = calculation_result["data"]
    return answer


def get_y(token, mode):
    status_1 = ""
    while status_1 != "success":
        y_1 = get_response_tukey(token, mode)
        status_1 = y_1["status"]
        print(status_1)
        if status_1 == "fail":
            sleep(0.2)
            return "Fail"
        print(y_1)
        sleep(2)
    data = y_1["prob"][0]["是"]
    return data


def get_predicted_value(data):
    # data_load = {}

    del data["Data_Analysis"]
    print(data)
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_token": "fc446a89-7924-40ef-8f88-8c81fc68413f",  # 模型api token
        "data": data,
    }

    token = get_api_tukey(headers, payload, "staging")  # 餵tukey
    y_1 = get_y(token, "staging")  # 得到預測值
    print(y_1)

    return y_1


def send_google_sheet(prob, index):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    SERVICE_ACCOUNT_FILE = "key.json"

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # If modifying these scopes, delete the file token.json.

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = "1G0hddt8WVx6VJ74R_flznvKtcxSoE_s97dSmF4F11UY"

    try:
        service = build("sheets", "v4", credentials=credentials)

        # Call the Sheets API
        sheet = service.spreadsheets()
        # result = (
        #     sheet.values()
        #     .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="in!A1:H24")
        #     .execute()
        # )
        # values = result.get("values", [])
        aoa = [[prob]]

        request = (
            sheet.values()
            .update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=f"test_data!L{index}",
                valueInputOption="USER_ENTERED",
                body={"values": aoa},
            )
            .execute()
        )

        print(request)
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    try:
        with open("marketing_test.json", encoding="utf-8") as f:
            data_load = json.load(f)
            if error in data_load:
                print("can't receive data from board")
    except Exception:
        print("can not load json")
    index = 2
    number = 0
    while True:
        prob = get_predicted_value(data_load[number])

        send_google_sheet(prob, index)

        index = index + 1

        number += 1
        if number == 100:
            break
