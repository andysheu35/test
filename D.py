from os import error

# import pyfirmata
import pandas as pd
import numpy as np
import requests
import json
from time import sleep
import random
from datetime import datetime as dt
from scipy import stats
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
    data = y_1["value"]
    return data


def get_predicted_value(number):
    data_load = {}
    try:
        with open("input.json") as f:
            data_load = json.load(f)
            if error in data_load:
                print("can't receive data from board")
    except Exception:
        print("can not load json")

    headers = {"Content-Type": "application/json"}
    payload = {
        "api_token": "7993323a-cfbd-4a7f-b696-a75ec683da94",  # 模型api token
        "data": data_load[number],
    }
    # data_load["AMB_WINDSPEED"] = random.uniform(1, 20)  # 產生假資料
    for i in data_load:
        i["AMB_WINDSPEED"] = float(i["AMB_WINDSPEED"])
    # print(payload)

    token = get_api_tukey(headers, payload, "qa")  # 餵tukey
    y_1 = get_y(token, "qa")  # 得到預測值
    print(y_1)

    # Grid_power性能指標
    match (number):
        case (number) if number <= 5:
            index = 0
        case (number) if number > 5 and number <= 11:
            index = 6
        case (number) if number > 11 and number <= 17:
            index = 12
        case (number) if number > 17 and number <= 23:
            index = 18
    real_grid = []
    data = data_load[index : index + 5]
    for i in data:
        real_grid.append(float(i["GRID_POWER"]))
    mean_true = float(data_load[number]["GRID_POWER"])
    mean_predict = y_1

    sd_true = np.std(real_grid)
    sd_predict = np.std(real_grid)

    modified_sd_true = np.sqrt(np.float32(6) / np.float32(5)) * sd_true
    modified_sd_predict = np.sqrt(np.float32(6) / np.float32(5)) * sd_predict

    (statistic, performance) = stats.ttest_ind_from_stats(
        mean1=mean_true,
        std1=modified_sd_true,
        nobs1=6,
        mean2=mean_predict,
        std2=modified_sd_predict,
        nobs2=6,
    )
    # 時間、即時風速、即時功率
    localtime = dt.now()
    localtime = localtime.isoformat()
    windspeed = data_load[number]["AMB_WINDSPEED"]
    real_power = data_load[number]["GRID_POWER"]
    print(windspeed)
    # 蒲氏溫度
    match (windspeed):
        case (windspeed) if windspeed >= 1 and windspeed < 1.5:
            beaufort = 1
        case (windspeed) if windspeed > 1.5 and windspeed < 4:
            beaufort = 2
        case (windspeed) if windspeed >= 4 and windspeed < 6:
            beaufort = 3
        case (windspeed) if windspeed >= 6 and windspeed < 8:
            beaufort = 4
        case (windspeed) if windspeed >= 8 and windspeed < 11:
            beaufort = 5
        case (windspeed) if windspeed >= 11 and windspeed < 14:
            beaufort = 6
        case (windspeed) if windspeed >= 14 and windspeed < 17.1:
            beaufort = 7
        case (windspeed) if windspeed >= 17.1 and windspeed < 20.7:
            beaufort = 8
        case (windspeed) if windspeed >= 20.7 and windspeed < 24.4:
            beaufort = 9
    return (
        y_1,
        localtime,
        windspeed,
        performance * 100,
        float(real_power) + random.uniform(1, 20),
        beaufort,
    )


def send_google_sheet(power, time, windspeed, performance, real_power, beaufort, index):
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
        # result = (
        #     sheet.values()
        #     .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="in!A1:H24")
        #     .execute()
        # )
        # values = result.get("values", [])
        aoa = [[power, time, windspeed, performance, real_power, beaufort]]

        request = (
            sheet.values()
            .update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=f"sheet!A{index}",
                valueInputOption="USER_ENTERED",
                body={"values": aoa},
            )
            .execute()
        )

        print(request)
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    number = 0
    index = 2
    while True:
        (
            power,
            times,
            windspeed,
            performance,
            real_power,
            beaufort,
        ) = get_predicted_value(number)

        send_google_sheet(
            power, times, windspeed, performance, real_power, beaufort, index
        )
        number = number + 1
        index = index + 1
        if number > 23:
            number = 0
