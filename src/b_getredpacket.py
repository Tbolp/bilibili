from b_login import *
import websocket
import ssl
import struct
import re
import asyncio
import requests

class DanMuProcess(object):

    def __init__(self):
        pass

    def process_danmu(self):
        pass

class DanMu(object):

    _url = "wss://broadcastlv.chat.bilibili.com:2245/sub"

    def __init__(self, id):
        self._roomId = id
        self.processer = None
        self._wss = None

    def connect(self):
        self._enter_room()
        loop = asyncio.get_event_loop()
        # asyncio.ensure_future(self._get_danmu())
        # asyncio.ensure_future(self._keep_hearts())
        loop.create_task(self._get_danmu())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            for i in asyncio.Task.all_tasks():
                print(i)
                print(i.cancel())
            loop.stop()
            loop.run_forever()
            loop.close()
        finally:
            self._wss.close()


    def _enter_room(self):
        self._wss = websocket.create_connection(self._url, sslopt={"cert_reqs": ssl.CERT_NONE})
        self._wss.send(self._generate_enter_frames(), websocket.ABNF.OPCODE_BINARY)

    def _change_room(self, id):
        self._wss.close()
        self._roomId = id
        print(self._roomId)
        self._enter_room()

    async def _get_danmu(self):
        while True:
            data = self._wss.recv()
            frames = self._analyze_frames(data)
            for i in frames:
                self.processer.process_danmu(i)
            await asyncio.sleep(0.2)

    async def _keep_hearts(self):
        while True:
            self._wss.send(DanMu._generate_heart_frames())
            await asyncio.sleep(25)

    def set_listener(self, listener):
        self.processer = listener

    @staticmethod
    def _analyze_frames(data):
        position = 0
        data_length = len(data)
        frames = []
        while position < data_length:
            length = struct.unpack(">I", data[position: position+4])[0]
            if data[position+8: position+12] == b'\x00\x00\x00\x05':
                try:
                    frames.append(json.loads(data[position+16: position+length].decode()))
                except UnicodeDecodeError:
                    print(data[position+16: position+length])
                    exit(-1)
            position = position + 16 + length
        return frames

    def _generate_enter_frames(self):
        data = json.dumps({"uid": 0, "roomid": self._roomId, "protover": 1, "platform": "web", "clientver": "1.2.6"})
        data = bytearray(data.encode())
        data = bytearray(b'\x00\x10\x00\x01\x00\x00\x00\x07\x00\x00\x00\x01') + data
        data = struct.pack('>I', len(data) + 4) + data
        return data

    @staticmethod
    def _generate_heart_frames():
        data = bytearray(b'\x00\x00\x00\x1f\x00\x10\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01') + bytearray("object Object".encode())
        return data

class RedPacket(DanMuProcess):

    def process_danmu(self, data):
        if data["cmd"] == "SYS_GIFT":
            if re.search("新春抽奖", data["msg_text"]):
                print("获得奖励")
                room_id = data["real_roomid"]
                print(data["url"])
                # self.get_redpacket(room_id)
        if data["cmd"] == "DANMU_MSG":
            print(data["info"][1])


    def get_redpacket(self, room_id):
        session = login.session
        # session.get("https://www.bilibili.com/plus/widget/ajaxGetCaptchaKey.php?js")
        custom_headers = {"Host": "api.live.bilibili.com",
                   "Origin": "http://live.bilibili.com",
                   # "Referer": "http://live.bilibili.com/1223",
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/57.0"}
        resp = session.get("http://api.live.bilibili.com/activity/v1/Raffle/check", params={"roomid": room_id})
        js_resp = json.loads(resp.text)
        raffle_id = js_resp["data"][0]["raffleId"]
        # requests.utils.add_dict_to_cookiejar(session.cookies, {"fts":str(int(time.time()))})
        # resp = session.get("http://api.live.bilibili.com/activity/v1/Common/welcomeInfo",params={"roomid":room_id})
        # print(resp.text)
        resp = session.get("http://api.live.bilibili.com/activity/v1/Raffle/join", params={"roomid":room_id, "raffleId":raffle_id}, headers=custom_headers)
        print(resp.status_code, resp.text)



# with Login.login() as login:
danmu = DanMu(66688)
danmu.set_listener(RedPacket())
danmu.connect()
