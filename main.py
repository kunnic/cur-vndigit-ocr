from __future__ import annotations

import cv2
import matplotlib.pyplot as plt

from src.preprocessing.preprocess import Preprocessing
from ocr.tesseract import TesseractOCR


IMAGE_PATH = "/app/data/input/preprocess/images/0074.png"


def show_image(image):
    plt.figure(figsize=(10, 10))
    plt.imshow(
        image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
        cmap="gray" if image.ndim == 2 else None,
    )
    plt.axis("off")
    plt.show()


def run_preprocess(img):
    pp = Preprocessing({
        "decide_engine": {"provider": None}
    })

    result = pp.process(img)

    print("=== PREPROCESS METADATA ===")
    print(result.metadata)
    print("=== PREPROCESS RESULT ===")
    print(result)

    return result


def run_tesseract(img):
    ocr = TesseractOCR()
    ocr_result = ocr.recognize(img)

    print("=== TESSERACT RESULT ===")
    print(ocr_result)

    return ocr_result


def run_paddle(img):
    try:
        from ocr.paddle import Paddle

        paddle_ocr = Paddle()
        paddle_result = paddle_ocr.recognize(img)

        print("=== PADDLE RESULT ===")
        print(paddle_result)

        return paddle_result
    except Exception as e:
        print("PaddleOCR failed, falling back to Tesseract:", e)
        return None


def main():
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {IMAGE_PATH}")

    print(f"Loaded image: {IMAGE_PATH}")
    print(f"Image shape: {img.shape}")

    preprocess_result = run_preprocess(img)

    print("=== SHOW PREPROCESSED IMAGE ===")
    show_image(preprocess_result.image)

    _ = run_tesseract(img)
    _ = run_paddle(img)


if __name__ == "__main__":
    main()