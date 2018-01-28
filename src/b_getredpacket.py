from b_login import *
from b_danmu import *
import re


class RedPacket(DanMuProcess):

    def __init__(self, login):
        self._login = login

    def process_danmu(self, data):
        if data["cmd"] == "SYS_GIFT":
            if re.search("新春抽奖", data["msg_text"]):
                print("开始获得奖励")
                room_id = data["real_roomid"]
                self.get_redpacket(room_id)
        # if data["cmd"] == "DANMU_MSG":
        #     print(data["info"][1])

    def get_redpacket(self, room_id):
        session = self._login.session
        custom_headers = {"Host": "api.live.bilibili.com",
                          "Origin": "http://live.bilibili.com",
                          "Referer": "http://live.bilibili.com/"+str(room_id),
                          "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/57.0"}
        resp = session.get("http://api.live.bilibili.com/activity/v1/Raffle/check", params={"roomid": room_id})
        js_resp = resp.json()
        try:
            raffle_id = js_resp["data"][0]["raffleId"]
        except IndexError:
            return
        # requests.utils.add_dict_to_cookiejar(session.cookies, {"fts":str(int(time.time()))})
        # resp = session.get("http://api.live.bilibili.com/activity/v1/Common/welcomeInfo",params={"roomid":room_id})
        # print(resp.text)
        # resp = session.post("https://api.live.bilibili.com/room/v1/Room/room_entry_action",
        #              data={"room_id": 793902, "platform": "pc"})
        # print(resp.text)
        resp = session.get("http://api.live.bilibili.com/activity/v1/Raffle/join", params={"roomid":room_id, "raffleId":raffle_id}, headers=custom_headers)
        print(resp.json()["msg"])
        print("当前红包数目： ",self.get_rednumber())

    def get_rednumber(self):
        session = self._login.session
        resp = session.get("https://api.live.bilibili.com/activity/v1/NewSpring/getRedBagNum", params={"_":get_time()})
        try:
            return resp.json()["data"]["red_bag_num"]
        except IndexError:
            return -1


if __name__ == "__main__":
    with Login.login() as login:
        danmu = DanMu(98284)
        danmu.set_listener(RedPacket(login))
        danmu.connect()
