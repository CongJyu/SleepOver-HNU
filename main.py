import requests
import base64
import json
import os

# get token
headers_1 = {
    "Cookie": "arccount62298=c; arccount62019=c",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66 "
}

# login and clock in
headers_2 = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": "fangkong.hnu.edu.cn",
    "Origin": "https://fangkong.hnu.edu.cn",
    "Referer": "https://fangkong.hnu.edu.cn/app/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75 "
}

# ocr
headers_3 = {
    "Host": "cloud.baidu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.76",
    "Accept": "*/*",
    "Origin": "https://cloud.baidu.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://cloud.baidu.com/product/ocr/general",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
}

# get variable
usr = os.getenv("usr")
pwd = os.getenv("pwd")
RealAddress = os.getenv("RealAddress")
ls = os.getenv("RealProvince_City_County").split(",")
RealCity = ls[1]
RealCounty = ls[2]
RealProvince = ls[0]


# step 1: get token and pics
def clockin():
    try:
        token_json = requests.get("https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode", headers=headers_1)
        if token_json.status_code != 200:
            print("Token geting failed, retrying...")
        while token_json.status_code != 200:
            token_json = requests.get("https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode", headers=headers_1)
        data = json.loads(token_json.text)
        token = data["data"]["Token"]
        img_url = "https://fangkong.hnu.edu.cn/imagevcode?token=" + token
        with open("img.jpg", "wb") as img:
            img.write(requests.get(img_url).content)

        # verifying code
        with open("img.jpg", "rb") as f:
            img = base64.b64encode(f.read())
        data = {
            "image": "data:image/jpeg;base64" + str(img)[2:-1],
            "img_url": "",
            "type": "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic",
            "detect_direction": "false"
        }
        response = requests.post('https://cloud.baidu.com/aidemo', headers=headers_3, data=data)
        result = response.json()["data"]["words_result"][0]["words"]
        # step 2: emulate login
        data = {
            "Code": usr,
            "Password": pwd,
            "Token": token,
            "VerCode": result
        }
        session = requests.Session()
        response = \
            session.post("https://fangkong.hnu.edu.cn/api/v1/account/login", headers=headers_2, data=json.dumps(data))
        incampus = response.json()["data"]["IsShowBackCampus"]
        if response.json()["code"] != 0:
            print("Verified code error.")
            clockin()
        else:
            # step 3: clock in
            data_1 = {
                "RealProvince": RealProvince,
                "RealCity": RealCity,
                "RealCounty": RealCounty,
                "RealAddress": RealAddress,
                "IsUnusual": "0",
                "UnusualInfo": "",
                "IsTouch": "0",
                "IsInsulated": "0",
                "IsSuspected": "0",
                "IsDiagnosis": "0",
                "tripinfolist": [
                    {
                        "aTripDate": "",
                        "FromAdr": "",
                        "ToAdr": "",
                        "Number": "",
                        "trippersoninfolist": []
                    }
                ],
                "toucherinfolist": [],
                "dailyinfo": {
                    "IsVia": "0",
                    "DateTrip": ""
                },
                "IsInCampus": "0",
                "IsViaHuBei": "0",
                "IsViaWuHan": "0",
                "InsulatedAdress": "",
                "TouchInfo": "",
                "IsNormalTemperature": "1"
            }
            data_2 = {
                "BackState": 1,
                "MorningTemp": "36.5",
                "NightTemp": "36.5",
                "RealAddress": RealAddress,
                "RealCity": RealCity,
                "RealCounty": RealCounty,
                "RealProvince": RealProvince,
                "tripinfolist": []
            }
            if incampus:
                print("在校")
                response = session.post("https://fangkong.hnu.edu.cn/api/v1/clockinlog/add", headers=headers_2,
                                        data=json.dumps(data_2))
            else:
                print("离校")
                response = session.post("https://fangkong.hnu.edu.cn/api/v1/clockinlog/add", headers=headers_2,
                                        data=json.dumps(data_1))
            msg = response.json()["msg"]
            print(msg)
    except Exception:
        print("Error")
        clockin()


if __name__ == "__main__":
    clockin()
