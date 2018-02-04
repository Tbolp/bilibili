import websockets
import struct
import asyncio
import json
import logging

logging.basicConfig(level=logging.WARNING,
                    format="%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s",
                    datefmt="%H:%M:%S",
                    filename="b_danmu.log",
                    filemode="w")


class DanMuProcess(object):

    def __init__(self):
        pass

    def process_danmu(self, data):
        pass


class DanMu(object):

    _url = "wss://broadcastlv.chat.bilibili.com:2245/sub"

    def __init__(self, id):
        self._roomId = id
        self._processor = DanMuProcess()
        self._wss = None

    def connect(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._connect())
        except KeyboardInterrupt:
            logging.info("exiting")
            for task in asyncio.Task.all_tasks():
                task.cancel()
            loop.run_forever()
            raise KeyboardInterrupt

    async def _connect(self):
        async with websockets.connect(DanMu._url) as wss:
            self._wss = wss
            await self._wss.send(self._generate_enter_frames())
            danmmu_task = asyncio.ensure_future(self._get_danmu())
            hearts_task = asyncio.ensure_future(self._keep_hearts())
            await asyncio.wait([danmmu_task, hearts_task])
            await danmmu_task

    async def _get_danmu(self):
        while True:
            try:
                data = await self._wss.recv()
            except:
                logging.warning("connection close")
                break
            frames = self._analyze_frames(data)
            for i in frames:
                self._processor.process_danmu(i)

    async def _keep_hearts(self):
        while True:
            try:
                await self._wss.send(self._generate_heart_frames())
            except:
                logging.warning("connection close")
                break
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
        return bytes(data)
