from os import error
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

    # try:
    #     with open("hour_1B.json") as f:
    #         data_load = json.load(f)
    #         if error in data_load:
    #             print("can't receive data from board")
    # except Exception:
    #     print("can not load json")
    with open("power.json", encoding="utf-8") as f:
        data_load = json.load(f)
    data = data_load[number]
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_token": "7b5552e0-1431-42b9-85b4-efa3127e4a64",  # 模型api token
        "data": data,
    }
    
    

    token = get_api_tukey(headers, payload, "staging")  # send to tukey
    y_1 = get_y(token, "staging")  # 得到預測值

    
    print(y_1)
    

    # 時間、即時風速、即時功率
    localtime = dt.now()
    localtime = localtime.isoformat()
    # 各錶點數值
    

    
    return(y_1)


def send_power_bi(
    times,
    performance,
    max,
    min,
    timelowerperform,
    motor_performance,
    water,
    other_performance,
    bearing_temp,
    windingR,
    windingS,
    windingT,
):
    url = "https://api.powerbi.com/beta/f572f9fa-fbc6-40b6-bb14-ccb10cd9a965/datasets/bb1bf29b-2f39-4faf-b9ea-f135eca68762/rows?ctid=f572f9fa-fbc6-40b6-bb14-ccb10cd9a965&key=OJdXgayvAwyo0Ez52uso%2B7XglOOXMMHgR4avzCJjH9dw7rl1iTu6BbZLF%2BwQs3zl25NQfh4S%2FyAtvG3lByT4jg%3D%3D"  # power bi url
    payload = json.dumps(
        [
            {
                "time": times,
                "設備整體性能": performance,
                "max": max,
                "min": min,
                "timelowerperformance": timelowerperform,
                "馬達性能": motor_performance,
                "冷卻水流量": water,
                "軸承溫度與水流量性能": other_performance,
                "軸承溫度": bearing_temp,
                "電機繞組Rphase": windingR,
                "電機繞組Sphase": windingS,
                "電機繞組Tphase": windingT,
            }
        ]
    )  # 參數格式
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def test(number):
    with open("compressor.json",encoding = "utf-8") as f:
        data = json.load(f)

    max = 100
    min = 0
    # 時間、即時風速、即時功率
    localtime = dt.now()
    localtime = localtime.isoformat()
    # 各錶點數值
    motor_temp = data[number]["MEVA_1TI_B303I_PV"]
    n1_temp = data[number]["MEVA_1TI_0609_2_PV"]
    n2_temp = data[number]["MEVA_1TI_0610_2_PV"]

    enter_pressure = data[number]["MEVA_1PI_0604_PV"]
    enter_temp = data[number]["MEVA_1TI_0601_PV"]
    first_exit_pressure = data[number]["MEVA_1PI_0603_PV"]
    second_exit_pressure = data[number]["MEVA_1PI_0605_PV"]
    performance = data[number]["performance"]
    motor = data[number]["motor"]
    enter = data[number]["enter"]
    exit = data[number]["exit"]
    
    
    return[performance,
        localtime,
        motor,
        enter,
        exit,
        motor_temp,n1_temp,n2_temp,enter_pressure,enter_temp,first_exit_pressure,second_exit_pressure,max,min]


def send_google_sheet(performance,index):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    SERVICE_ACCOUNT_FILE = "key.json"

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # If modifying these scopes, delete the file token.json.

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = "1gMTsOJde7YyAmxF0myfXqs4YcVDQfG1HjLwW5LZMS3Y"

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
        aoa = [[performance]]

        request = (
            sheet.values()
            .update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=f"sheet!P{index}",
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
    with open("power.json", encoding="utf-8") as f:
        data_load = json.load(f)
    
    # while True:
    #     data_raw = []
    #     for i in range(1):
    #         row = test(number)
            
    #         data_raw.append(row)
            
    #         print("Raw data - ", data_raw)
        
    #     performance = data_raw[0][0]
    #     if performance < 40:
    #         timelowerperform += 1
    #     else:
    #         timelowerperform = 0
    #     data_raw[0].append(timelowerperform)
    #     # set the header record
    #     HEADER = ["設備整體性能", "time", "馬達性能", "入口處性能","出口處性能","馬達溫度","N1溫度","N2溫度","入口壓力指示","入口溫度指示","第一段出口壓力","第二段出口壓力","maxperform","minperform","timelowerperformance"]
        
    #     data_df = pd.DataFrame(data_raw, columns=HEADER)
    #     data_json = bytes(data_df.to_json(orient='records'), encoding='utf-8')
    #     print("JSON dataset", data_json)

    #     # Post the data on the Power BI API
    #     req = requests.post(url, data_json)

    #     print("Data posted in Power BI API")
        
        
    #     number += 1
    #     if number > 100:
    #         number = 1
    #     sleep(1.5)
    while True:
        (
            performance
        ) = get_predicted_value(number)

        send_google_sheet(
            performance,index
        )
        number = number + 1
        index = index + 1
        if number > len(data_load)-1:
            break
 