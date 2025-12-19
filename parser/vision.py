from paddleocr import PaddleOCR
import cv2

ocr = PaddleOCR(use_angle_cls=True, lang="en")

def vision_ocr(image_path):
    img = cv2.imread(image_path)
    result = ocr.predict(img)
    text = []
    for line in result:
        for word in line:
            text.append(word[1][0])
    return "\n".join(text)
