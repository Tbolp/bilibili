from b_danmu import *

class ShowDanmu(DanMuProcess):
    def process_danmu(self, data):
        print(data)

if __name__ == "__main__":
    try:
        while True:
            id = input("输入房间号: ")
            try:
                id = int(id)
                break
            except ValueError:
                print("输入错误，重新输入")
    except KeyboardInterrupt:
        print("退出")

    danmu = DanMu(id)
    danmu.set_listener(ShowDanmu())
    try:
        danmu.connect()
    except KeyboardInterrupt:
        print("结束")
