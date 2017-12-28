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
    r = _get_finger(img)
    res = []
    for i in range(10):
        with open("finger/" + str(i), "r") as f:
            rc = json.load(f)
        res.append(abs(sum(map(lambda x: x[0] - x[1], zip(r, rc)))))
    n = res.index(min(res))
    if n == 0:
        for i in range(img.size[1]):
            if i == 0:
                return 8
    return n

def _rec_sig(img):
    r = _get_finger(img)
    if r[0] < 50:
        return '-'
    return '+'

class Capture(object):

    def __init__(self, content):
        if isinstance(content, str):
            image = Image.open(content)
            image = image.convert("L")
            self._image = Image.eval(image, lambda x: 1 if x<100 else 0)
        else:
            pass

    def get_result(self):
        imgs = self._split_image()
        a = _rec_num(imgs[0])*10 + _rec_num(imgs[1])
        b = _rec_num(imgs[3])
        if _rec_sig(imgs[2]) == '-':
            return a - b
        return a + b

    def _split_image(self):
        def test(i):
            for j in range(img.size[1]):
                if img.getpixel((i, j)) == 1:
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


c = Capture("2.jpeg")
imgs = c._split_image()
for i in range(4):
    imgs[i].save("finger/"+str(i)+".jpeg")
# print(c.get_result())
