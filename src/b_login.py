import pyqrcode
import requests
import time
import http.cookiejar
from b_capture import *


def save_cookie(c, fn):
    with open(fn, "w") as f:
        d = requests.utils.dict_from_cookiejar(c)
        json.dump(d, f)


def load_cookie(fn):
    with open(fn, "r") as f:
        d = json.load(f)
        return requests.utils.cookiejar_from_dict(d)

# 13位数
def get_time():
    return int(round((time.time()*1000)))


class Login(object):

    @property
    def session(self):
        return self._session

    def __init__(self, cookie_fn = "cookie"):
        self._session = requests.session()
        self._cookie_fn = cookie_fn
        try:
            self._session.cookies = load_cookie(cookie_fn)
        except:
            self._session.cookies = http.cookiejar.CookieJar()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save_cookie(self._session.cookies, self._cookie_fn)

    def is_login(self):
        session = self._session
        try:
            resp = session.get("https://api.live.bilibili.com/FreeSilver/getCurrentTask")
            info = json.loads(resp.text)
            if info["code"] == -101:
                return False
            else:
                return True
        # except FileNotFoundError:
        #     return False
        except:
            return False

    @classmethod
    def login(cls, cookie_fn = "cookie"):
        login = Login(cookie_fn=cookie_fn)
        if login.is_login():
            return login
        print("二维码已被保存到 QRCode.png")
        key = login._get_qrcode()
        session = login.session
        try:
            while True:
                url = "https://passport.bilibili.com/qrcode/getLoginInfo"
                data = {"oauthKey": key,
                        "gourl": "https://www.bilibili.com/"}
                r = session.post(url, data=data)
                info = r.json()
                if info["status"]:
                    print("登录成功")
                    return login
                elif info["data"] == -2:
                    print("二维码已更新,Ctrl+C 可退出")
                    key = login._get_qrcode()
                time.sleep(5)
        except KeyboardInterrupt:
            print("再见")
        return None

    def _get_qrcode(self, fn="QRCode.png"):
        resp = self._session.get("https://passport.bilibili.com/qrcode/getLoginUrl")
        info = resp.json()
        url = info["data"]['url']
        key = info["data"]["oauthKey"]
        qrcode = pyqrcode.create(url)
        # print(qrcode.terminal(quiet_zone=2))
        qrcode.png(fn)
        return key
