import cv2
import pytesseract
from config import LANGUAGE

def ocr_image(filename):
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang=LANGUAGE)
    return text.strip()