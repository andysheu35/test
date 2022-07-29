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
    with open("hour_1B.json", encoding="utf-8") as f:
        data_load = json.load(f)
    data = data_load[number]
    del data["id"]
    del data["time"]
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_token": "79664e30-4e4e-40df-8666-4d58f3aa158f",  # 模型api token
        "data": data,
    }
    payload_motor = {
        "api_token": "b984af6a-0754-4a7e-8464-f6c8d586605b",  # 模型api token
        "data": data,
    }
    payload_enter = {
        "api_token": "41da5c0f-3555-43a9-89f9-bedf913a6430",  # 模型api token
        "data": data,
    }
    payload_exit = {
        "api_token": "5263de7c-64f2-420c-aa01-64cbcde23538",  # 模型api token
        "data": data,
    }

    token = get_api_tukey(headers, payload, "staging")  # send to tukey
    y_1 = get_y(token, "staging")  # 得到預測值

    motor_token = get_api_tukey(headers, payload_motor, "staging")
    enter_token = get_api_tukey(headers, payload_enter, "staging")
    exit_token = get_api_tukey(headers, payload_exit, "staging")

    motor_output = get_y(motor_token, "staging")
    enter_output = get_y(enter_token, "staging")
    exit_output = get_y(exit_token, "staging")
    print(y_1)
    print(motor_output)
    print(enter_output)
    print(exit_output)

    # 時間、即時風速、即時功率
    localtime = dt.now()
    localtime = localtime.isoformat()
    # 各錶點數值
    motor_temp = data["MEVA_1TI_B303I_PV"]
    n1_temp = data["MEVA_1TI_0609_2_PV"]
    n2_temp = data["MEVA_1TI_0610_2_PV"]

    enter_pressure = data["MEVA_1PI_0604_PV"]
    enter_temp = data["MEVA_1TI_0601_PV"]
    first_exit_pressure = data["MEVA_1PI_0603_PV"]
    second_exit_pressure = data["MEVA_1PI_0605_PV"]

    return (
        y_1 * 100,
        localtime,
        motor_output * 100,
        enter_output * 100,
        exit_output * 100,
        motor_temp,
        n1_temp,
        n2_temp,
        enter_pressure,
        enter_temp,
        first_exit_pressure,
        second_exit_pressure,
    )


def send_power_bi(
    times,
    performance,
    max,
    min,
    timelowerperform,
    motor_performance,
    enter_performance,
    exit_performance,
    n1_temp,
    n2_temp,
    motor_temp,
    enter_pressure,
    enter_temp,
    first_exit_pressure,
    second_exit_pressure,
):
    url = "https://api.powerbi.com/beta/f572f9fa-fbc6-40b6-bb14-ccb10cd9a965/datasets/94b1fa8e-c1e4-4d73-a1c0-7c097d267d1f/rows?key=gHO0d2AT5THrj662348Do1aySr0NeP9TU%2BRWA61C4DpfCo8QpfpLajPdMg1QbnP0%2BWV%2BYxDtjJ6%2BByrYK1EYSg%3D%3D"  # power bi url
    payload = json.dumps(
        [
            {
                "time": times,
                "設備整體性能": performance,
                "maxperform": max,
                "minperform": min,
                "timelowerperformance": timelowerperform,
                "馬達性能": motor_performance,
                "入口處性能": enter_performance,
                "出口處性能": exit_performance,
                "馬達溫度": motor_temp,
                "N1溫度": n1_temp,
                "N2溫度": n2_temp,
                "入口壓力指示": enter_pressure,
                "入口溫度指示": enter_temp,
                "第一段出口壓力": first_exit_pressure,
                "第二段出口壓力": second_exit_pressure,
            }
        ]
    )  # 參數格式
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


if __name__ == "__main__":
    number = 1
    with open("hour_1B.json", encoding="utf-8") as f:
        data = json.load(f)
    max = 100
    min = 0
    timelowerperformance = 0
    while True:
        (
            performance,
            times,
            motor_performance,
            enter_performance,
            exit_performance,
            motor_temp,
            n1_temp,
            n2_temp,
            enter_pressure,
            enter_temp,
            first_exit_pressure,
            second_exit_pressure,
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
            enter_performance,
            exit_performance,
            n1_temp,
            n2_temp,
            motor_temp,
            enter_pressure,
            enter_temp,
            first_exit_pressure,
            second_exit_pressure,
        )
        number += 1
        if number > len(data) - 1:
            number = 1
