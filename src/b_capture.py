from PIL import Image
import json


def _get_finger(img):
    w, h = img.size
    data1 = img.getdata()
    r1 = sum(data1)
    data2 = img.crop((0, 0, w, int(h / 2))).getdata()
    r2 = sum(data2)
    data3 = img.crop((0, int(h / 2), w, h)).getdata()
    r3 = sum(data3)
    return [r1, r2, r3]


def _rec_num(img):
    # r = _get_finger(img)
    # res = []
    # for i in range(10):
    #     with open("finger/" + str(i), "r") as f:
    #         rc = json.load(f)
    #     res.append(abs(sum(map(lambda x: x[0] - x[1], zip(r, rc)))))
    # n = res.index(min(res))
    # if n == 0:
    #     for i in range(img.size[1]):
    #         if i == 0:
    #             return 8
    # return n
    pass

def _rec_sig(img):
    r = _get_finger(img)
    if r[0] < 50:
        return '-'
    return '+'

class Capture(object):

    def __init__(self):
        self._fingers = []
        for i in range(10):
            image = Image.open("finger/"+str(i)+".bmp")
            self._fingers.append(image)

    def load_file(self, fn):
        image = Image.open(fn)
        image = image.convert("L")
        self._image = Image.eval(image, lambda x: 0 if x < 200 else 255)

    def get_result(self):
        imgs = self._split_image()
        a = self._rec_num(imgs[0])*10 + self._rec_num(imgs[1])
        b = self._rec_num(imgs[3])
        if self._rec_sig(imgs[2]) == '-':
            return a - b
        return a + b

    def _rec_sig(self, img):
        res = sum(img.getdata())
        if res < 100000:
            return '-'
        return '+'

    def _rec_num(self, img):
        if img.size[0] < 10:
            return 1;
        width = min(16, img.size[0])
        height = min(40, img.size[1])
        res = []
        for i in range(10):
            if i == 1:
                res.append(25500)
                continue
            sum = 0
            for x in range(width):
                for y in range(height):
                   sum = sum + abs(img.getpixel((x, y)) - self._fingers[i].getpixel((x, y)))
            res.append(sum)
        n = res.index(min(res))
        return n;


    def _split_image(self):
        def test(i):
            for j in range(img.size[1]):
                if img.getpixel((i, j)) == 0:
                    return False
            return True
        img = self._image
        x = img.size[0]
        y = img.size[1]
        points = [0]
        images = []
        flag = test(0)
        for i in range(x):
            t = test(i)
            if flag != t:
                flag = t
                points.append(i)
        for i in range(1, 9, 2):
            images.append(img.crop((points[i], 0, points[i+1], y)))
        return images

