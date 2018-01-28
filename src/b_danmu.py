import websocket
import ssl
import struct
import asyncio
import json


class DanMuProcess(object):

    def __init__(self):
        pass

    def process_danmu(self, data):
        pass


class DanMu(object):

    _url = "wss://broadcastlv.chat.bilibili.com:2245/sub"

    def __init__(self, id):
        self._roomId = id
        self._processor = None
        self._wss = None

    def connect(self):
        self._enter_room()
        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(self._get_danmu(), self._keep_hearts(), return_exceptions=KeyboardInterrupt())
        try:
            loop.run_until_complete(tasks)
        except KeyboardInterrupt:
            tasks.cancel()
            loop.stop()
            loop.run_forever()
        finally:
            loop.close()
            self._wss.close()

    def _enter_room(self):
        self._wss = websocket.create_connection(self._url, sslopt={"cert_reqs": ssl.CERT_NONE})
        self._wss.settimeout(1)
        self._wss.send(self._generate_enter_frames(), websocket.ABNF.OPCODE_BINARY)

    def _change_room(self, id):
        self._wss.close()
        self._roomId = id
        print(self._roomId)
        self._enter_room()

    async def _get_danmu(self):
        while True:
            try:
                data = self._wss.recv()
                frames = self._analyze_frames(data)
                for i in frames:
                    self._processor.process_danmu(i)
            except websocket.WebSocketTimeoutException:
                pass
            await asyncio.sleep(0.2)

    async def _keep_hearts(self):
        while True:
            self._wss.send(DanMu._generate_heart_frames())
            await asyncio.sleep(30)

    def set_listener(self, listener):
        self._processor = listener

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
