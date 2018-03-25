from PIL import Image
from pytesseract import pytesseract
import base64
import pandas as pd
import find


# Main function, call this function only!
# @param img_path str: The path of image, can be absolute or comparative
# @return str: The string that is the closest to the position you choose
def closest_word(img_path):
    position = find.get_qr_top(img_path)
    crop_image(img_path, position[0], position[1])
    img = Image.open("img.png")
    width, height = img.size
    raw_word = closest_in_series(img_to_series("img.png"), width // 2, height)
    return trim_word(raw_word)


# Don't call functions below!
def load_img_bytes(base64_img):
    file = open("img.png", "wb")
    file.write(base64.decodebytes(base64_img))
    file.close()


def crop_image(img_path, x, y):
    img = Image.open(img_path)
    width, height = img.size
    region = []
    if x - 150 < 0:
        region.append(0)
    else:
        region.append(x - 150)

    if y - 300 < 0:
        region.append(0)
    else:
        region.append(y - 150)

    if x + 150 > width:
        region.append(width)
    else:
        region.append(x + 150)

    region.append(y)

    region = tuple(region)
    crop_img = img.crop(region)
    crop_img.save("img.png")


def img_to_series(img_name):
    data = pytesseract.image_to_data(Image.open(img_name, "r").convert("L"))
    save_file = open("data.tsv", "w")
    save_file.write(data)
    save_file.close()
    return pd.read_csv("data.tsv", sep="\t")


def dist(x1, y1, x2, y2):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


def get_center(left, top, width, height):
    x = int(left + width / 2)
    y = int(top - height - 2)
    return x, y


def closest_in_series(series, x, y):
    min_dist = -1
    min_word = None
    for i in range(len(series)):
        curr = series.iloc[i]
        if curr["conf"] == -1:
            continue
        curr_center = get_center(curr["left"], curr["top"], curr["width"], curr["height"])
        temp_dist = dist(x, y, curr_center[0], curr_center[1])
        if min_dist == -1 or temp_dist < min_dist:
            min_dist = temp_dist
            min_word = curr["text"]
    return min_word


def find_top(series):
    top = 1000
    top_num = None
    for i in range(len(series)):
        curr = series.iloc[i]
        if curr["conf"] == -1 or (not is_num(curr["text"])):
            continue
        temp = curr["top"]
        if temp < top:
            top = temp
            top_num = int(curr["text"])
    return top_num


def trim_word(s):
    low = 0
    high = len(s) - 1
    while not s[low].isalpha():
        low += 1
    while not s[high].isalpha():
        high -= 1
    return s[low:high + 1]

def is_num(s):
    for c in s:
        if not c.isdigit():
            return False
    return True

# test
print(closest_word("test1.png"))