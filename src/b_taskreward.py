from b_login import *


class TaskReward(object):

    def __init__(self, login):
        self._session = login.session
        self._capture = Capture()

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
            self._get_single_reward(info["time_start"], info["time_end"])
            time.sleep(60)

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
            count = count + 1
            r = s.get("https://api.live.bilibili.com/FreeSilver/getAward?time_start="+str(start)+"&end_time="+str(end)+"&captcha="+str(n))
            info = json.loads(r.text)
            if info["code"] == 0:
                print("已成功领取"+str(info["data"]["awardSilver"])+"个瓜子")
                break;
            elif info["code"] == -902:
                print("验证码错误！")
                count = count + 1
            elif info["code"] == -901:
                print("验证码过期")
            time.sleep(5);

    def _get_capture_data(self):
        r = self._session.get("https://api.live.bilibili.com/freeSilver/getCaptcha?ts=" + str(get_time()))
        with open("capture.jpeg", "wb") as f:
            f.write(r.content)
        self._capture.load_file("capture.jpeg");
        print("开始尝试。。。")
        return self._capture.get_result()

    def _get_capture_data_manual(self):
        r = self._session.get("https://api.live.bilibili.com/freeSilver/getCaptcha?ts=" + str(get_time()))
        with open("capture.jpeg", "wb") as f:
            f.write(r.content)
        print("验证码已保存到 capture.jpeg")
        return input("输入验证码: ")


with Login.login() as l:
    task = TaskReward(l)
    task.get_reward()