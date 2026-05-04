import numpy as np
import cv2

from .blank import BlankDetector
from .code import CodePreprocessor

# pipeline_config = {
#     "blank_detector": {
#         "model_path": "models/rf_blank_v1.joblib", 
#         "threshold": 0.65,
#         "lower": 0.01,
#         "upper": 0.98
#     },

#     "code_detector": {
#         "types": ["QRCODE", "CODE128"]
#     }
# }

class Preprocessing:
    def __init__(self, config: dict = None):
        self.config = config if config is not None else {}

        blank_config = self.config.get('blank_detector', {})
        code_config = self.config.get('code_preprocessor', {})

        self.blank_detector = BlankDetector(**blank_config)
        self.code_preprocessor = CodePreprocessor(**code_config)
    
    @staticmethod
    def process(image: np.ndarray) -> np.ndarray:
        if image is None or image.size == 0:
            return image 

    def _process(self, image: np.ndarray) -> np.ndarray:
        # 1. RBG -> Grayscale
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 2. Denoising by appying Gaussian Blur
        # arguments: (input image, kernel size, sigmaX)
        blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)

        # 3. Deskewing
        # arguments: (input image, threshold value, max value, thresholding type)
        _, bw = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(bw > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(grayscale, M, (w, h))

        # 4. Autocropping
        # arguments: (input image, threshold value, max value, thresholding type)
        _, thresh = cv2.threshold(
            deskewed, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        coords = cv2.findNonZero(thresh)

        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            cropped = deskewed[y:y+h, x:x+w]
        else:
            # fallback: giữ nguyên ảnh
            cropped = deskewed

        if len(cropped.shape) == 3:
            cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

        # 5. Processing yellowish background, unbalanced brightness/contrast,
        # etc. by applying adaptive thresholding
        # arguments: (input image, max value, adaptive method, thresholding type, block size, C)
        normalized =  cv2.adaptiveThreshold(
            cropped, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )

        # 6. Sharpening by applying unsharp masking
        # arguments: (input image, output image, kernel size, sigmaX)
        kernel = np.array([[0, -1, 0],
                   [-1, 5,-1],
                   [0, -1, 0]])
        sharpened = cv2.filter2D(normalized, -1, kernel)

        return sharpened
    
    def 