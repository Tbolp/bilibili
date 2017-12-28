import pyqrcode
import requests
import pickle
import json
import time

def save_cookie(c, fn):
    with open(fn, "wb") as f:
        pickle.dump(requests.utils.dict_from_cookiejar(c), f)

def load_cookie(fn):
    with open(fn, "rb") as f:
        return requests.utils.cookiejar_from_dict(pickle.load(f))

def get_time():
    return int(round((time.time()*1000)))

class Login(object):

    def __init__(self):
        self._session = requests.session()
        self._cookie_fn = "cookie"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save_cookie(self._session.cookies, self._cookie_fn)
        pass

    def _is_login(self):
        session = self._session
        try:
            session.cookies = load_cookie(self._cookie_fn)
            resp = session.get("https://api.live.bilibili.com/FreeSilver/getCurrentTask")
            info = json.loads(resp.text)
            if info["code"] == -101:
                return False
            else:
                return True
        except FileNotFoundError:
            return False
        else:
            return False

    def login(self):
        if self._is_login():
            return True
        key = self._get_qrcode("二维码已被保存到 QRCode.png,Ctrl+C 可退出")
        session = self._session
        try:
            while True:
                url = "https://passport.bilibili.com/qrcode/getLoginInfo"
                data = {"oauthKey": key,
                        "gourl": "https://www.bilibili.com/"}
                r = session.post(url, data=data)
                info = json.loads(r.text)
                if info["status"]:
                    print("登录成功")
                    return True
                elif info["data"] == -2:
                    key = self._get_qrcode("二维码已更新,Ctrl+C 可退出")
                time.sleep(5)
        except KeyboardInterrupt:
            print("再见")
        return False

    def get_reward(self):
        session = self._session
        while True:
            print("开始领取奖励")
            resp = session.get("https://api.live.bilibili.com/FreeSilver/getCurrentTask")
            info = json.loads(resp.text)
            if info["code"] == -10017:
                print(info["msg"])
                break
            info = info["data"]
            self._get_single_reward(info["time_start"], info["time_end"], counts=0)

    def _get_single_reward(self, start, end, counts=3, manual=True):
        s = self._session
        detal = end - start + 10
        time.sleep(detal)
        count = 0
        while True:
            if count < counts:
                n = self._get_capture_data()
            elif manual:
                n = self._get_capture_data_manual()
            else:
                print("已放弃本次奖励")
                break;
            r = s.get("https://api.live.bilibili.com/FreeSilver/getAward?time_start="+str(start)+"&end_time="+str(end)+"&captcha="+n)
            info = json.loads(r.text)
            if info["code"] == 0:
                print("已成功领取"+str(info["data"]["awardSilver"])+"个瓜子")
                break;
            elif info["code"] == -902:
                print("验证码错误！")
                count = count + 1
            elif info["code"] == -901:
                print("验证码过期")

    def _get_capture_data(self):
        return "10"

    def _get_capture_data_manual(self):
        r = self._session.get("https://api.live.bilibili.com/freeSilver/getCaptcha?ts=" + str(get_time()))
        with open("capture.jpeg", "wb") as f:
            f.write(r.content)
        print("验证码已保存到 capture.jpeg")
        return input("输入验证码: ")

    def _get_qrcode(self, msg = ""):
        resp = self._session.get("https://passport.bilibili.com/qrcode/getLoginUrl")
        info = json.loads(resp.text)
        url = info["data"]['url']
        key = info["data"]["oauthKey"]
        qrcode = pyqrcode.create(url)
        # print(qrcode.terminal(quiet_zone=2))
        qrcode.png("QRCode.png")
        if msg:
            print(msg)
        return key

with Login() as l:
    if l.login():
        l.get_reward()
