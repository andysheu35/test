from os import error
import pandas as pd
import numpy as np
import requests
import json
from time import sleep
import random
from datetime import datetime as dt
from scipy import stats


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
    data = y_1["prob"][0]["1"]
    return data


def get_predicted_value(number):

    # try:
    #     with open("hour_1B.json") as f:
    #         data_load = json.load(f)
    #         if error in data_load:
    #             print("can't receive data from board")
    # except Exception:
    #     print("can not load json")
    with open("cooling_tower.json", encoding="utf-8") as f:
        data_load = json.load(f)
    data = data_load[number]
    del data["id"]
    del data["time"]
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_token": "74c279c5-8ea7-4864-bfbe-bb65645d8687",  # 模型api token
        "data": data,
    }
    payload_motor = {
        "api_token": "d7af687c-6889-421b-b371-27478b8fcf52",  # 模型api token
        "data": data,
    }
    payload_other = {
        "api_token": "23156864-288f-464f-94ea-07a3b50ac407",  # 模型api token
        "data": data,
    }

    token = get_api_tukey(headers, payload, "staging")  # send to tukey
    y_1 = get_y(token, "staging")  # 得到預測值

    motor_token = get_api_tukey(headers, payload_motor, "staging")
    other_token = get_api_tukey(headers, payload_other, "staging")

    motor_output = get_y(motor_token, "staging")
    other_output = get_y(other_token, "staging")

    print(y_1)
    print(motor_output)
    print(other_token)

    # 時間、即時風速、即時功率
    localtime = dt.now()
    localtime = localtime.isoformat()
    # 各錶點數值
    water = data["JNAOH_FI1000A_PV"]
    bearing_temp = data["JNAOH_TI_B1000YF1_1_PV"]
    windingR = data["JNAOH_TI_B1000YF2_R_PV"]
    windingS = data["JNAOH_TI_B1000YF2_S_PV"]
    windingT = data["JNAOH_TI_B1000YF2_T_PV"]

    return (
        y_1 * 100,
        localtime,
        motor_output * 100,
        other_output * 100,
        water,
        bearing_temp,
        windingR,
        windingS,
        windingT,
    )


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


if __name__ == "__main__":
    number = 1
    with open("cooling_tower.json", encoding="utf-8") as f:
        data = json.load(f)
    max = 100
    min = 0
    while True:
        (
            performance,
            times,
            motor_performance,
            other_performance,
            water,
            bearing_temp,
            windingR,
            windingS,
            windingT,
        ) = get_predicted_value(number)
        if performance < 25:
            timelowerperformance += 1
        else:
            timelowerperformance = 0
        send_power_bi(
            times,
            performance,
            max,
            min,
            timelowerperformance,
            motor_performance,
            water,
            other_performance,
            bearing_temp,
            windingR,
            windingS,
            windingT,
        )
        number += 1
        if number > len(data) - 1:
            number = 1
 