import json
import os
import time

import requests

import dingPush


def getAccessToken(session, openid):
    time_stamp = str(int(time.time()))  #获取时间戳
    url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/login/we-chat/callback?callback=https%3A%2F%2Fqczj.h5yunban.com%2Fqczj-youth-learning%2Findex.php&scope=snsapi_userinfo&appid=wx56b888a1409a2920&openid=" + openid + "&nickname=ZhangSan&headimg=&time=" + time_stamp + "&source=common&sign=&t=" + time_stamp
    res = session.get(url)
    access_token = res.text[45:81]
    print("INFO: 获取到AccessToken:", access_token)
    return access_token


def getCurrentCourse(session, access_token):
    url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/common-api/course/current?accessToken=" + access_token
    res = session.get(url)
    res_json = json.loads(res.text)
    if (res_json["status"] == 200):
        print("INFO: 获取到最新课程代号:", res_json["result"]["id"])
        return res_json["result"]["id"]
    else:
        raise Exception("INFO: 获取最新课程失败！")


def getJoin(session, access_token, current_course, nid, cardNo):
    data = {
        "course": current_course,  # 大学习期次的代码，如C0046，本脚本已经帮你获取啦
        "subOrg": None,
        "nid": nid,  # 团组织编号，形如N003************
        "cardNo": cardNo  # 打卡昵称
    }
    url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/join?accessToken=" + access_token
    res = session.post(url, json=data)
    print("INFO: 签到结果:", res.text)
    res_json = json.loads(res.text)
    if (res_json["status"] == 200):
        print("INFO: 签到成功")
        return res.text, True
    else:
        raise Exception("INFO: 签到失败！")


if __name__ == '__main__':
    nid = os.getenv("nid")
    cardNo = os.getenv("cardNo")
    openid = os.getenv("openid")

    session = requests.session()
    session.headers = {
        'User-Agent':
        'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4'
    }
    try:
        checkFlag = False

        # 获取token
        time.sleep(5)
        access_token = getAccessToken(session, openid)

        # 获取最新的章节
        time.sleep(5)
        current_course = getCurrentCourse(session, access_token)

        # 签到
        time.sleep(5)
        res, checkFlag = getJoin(session, access_token, current_course, nid,
                                 cardNo)

        DD_BOT_TOKEN = os.getenv("DD_BOT_TOKEN")
        DD_BOT_SECRET = os.getenv("DD_BOT_SECRET")
        res = json.loads(res)
        dingpush = dingPush.dingpush(
            "青年大学习签到结果",
            "青年大学习签到成功：\n" + "状态码：" + str(res["status"]) + "\n课程ID: " +
            current_course + "\n签到学号: " + res["result"]["cardNo"] +
            "\n签到时间: " + res["result"]["lastUpdTime"], "", DD_BOT_TOKEN,
            DD_BOT_SECRET)
        dingpush.SelectAndPush()
    except Exception as e:
        print("WARNING: " + str(e))
        try:
            dingPush = dingPush.dingpush(
                "青年大学习签到结果",
                "青年大学习签到出现问题：\n" + str(e) + "\n是否完成签到：" + str(checkFlag), "",
                DD_BOT_TOKEN, DD_BOT_SECRET)
        except Exception as e:
            print("ERROR: " + str(e))