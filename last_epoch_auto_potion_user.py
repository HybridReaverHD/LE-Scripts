import cv2
from pytesseract import pytesseract
import pyscreenshot
import pygetwindow
from PIL import Image
import re
import numpy as np
from pyautogui import press

pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

WINDOW_NAME = "Last Epoch"
DEBUG = False
HP_THRESHOLD = 0.6

def get_last_epoch_screenshot() -> Image:
    # Get the window with the title "Your Window Title"
    window = pygetwindow.getWindowsWithTitle(WINDOW_NAME)[0]

    # Get the window coordinates
    x1, y1, x2, y2 = window.left, window.top, window.left + window.width, window.top + window.height

    # Capture the specified window
    im = pyscreenshot.grab(bbox=(x1, y1, x2, y2))
    # im.show()

    return im


def crop_screenshot_to_hp(screenshot: Image):
    base_x, base_y = 457, 987
    len_x, len_y = 111, 19
    img_left_area = (base_x, base_y, base_x + len_x, base_y + len_y)
    hp_sc = screenshot.crop(img_left_area)

    # hp_sc.show()

    return hp_sc


def convert_from_image_to_cv2(pil_img: Image) -> np.ndarray:
    cv2_arr = np.array(pil_img)
    cv2_img = cv2.cvtColor(cv2_arr, cv2.COLOR_RGB2BGR)

    return cv2_img


def convert_from_cv2_to_image(cv2_img: np.ndarray) -> Image:
    cv2_img_arr = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cv2_img_arr)

    return pil_img


def get_hp_variants_from_hp_screenshot(screenshot: Image):
    # Read the image
    image = convert_from_image_to_cv2(screenshot)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    return thresh, gray, image


def get_hp_str_from_hp_dilate(dilate):
    # Apply OCR using Tesseract
    numbers = pytesseract.image_to_string(dilate, config='--psm 6')

    return numbers


def filter_hp_string_to_tuple(hp_str):
    num_list = re.findall("\\d+", hp_str)
    try:
        hp_cur = num_list[0]
        hp_max = num_list[1]
    except:
        return 0, 0

    return int(hp_cur), int(hp_max)


def trigger_potion():
    if DEBUG:
        print(f"trigger potion")

    press('1')


def save_error(cv2_img: Image, name: str, count: int):
    jpg_path = f"C:\\Users\\KrampusHD\\Pictures\\le_err_{count}_{name}.jpg"
    pil_img = convert_from_cv2_to_image(cv2_img)
    pil_img.save(jpg_path)


def main():
    err_count = 0

    while True:
        sc = get_last_epoch_screenshot()
        hp_sc = crop_screenshot_to_hp(sc)
        thresh, gray, image = get_hp_variants_from_hp_screenshot(hp_sc)
        hp_str = get_hp_str_from_hp_dilate(gray)
        hp_cur, hp_max = filter_hp_string_to_tuple(hp_str)

        if hp_max < 10:
            if DEBUG:
                save_error(thresh, "thresh", err_count)
                save_error(gray, "gray", err_count)
                save_error(image, "image", err_count)
                print(f"ERROR: C:\\Users\\KrampusHD\\Pictures\\le_err_{err_count}_* {hp_str}")

                err_count += 1
            continue

        if DEBUG:
            print(f"HP: {hp_cur} | {hp_max}")

        if hp_cur < hp_max * HP_THRESHOLD:
            trigger_potion()


if __name__ == "__main__":
    main()
