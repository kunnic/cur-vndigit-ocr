import joblib
import numpy as np
from typing import Tuple
from strategies.base import IBlankDetector
import cv2

class BlankDetector(IBlankDetector):
    def __init__(
        self,
        model_path: str,
        threshold: float = 0.5,
        lower: float = 0.005,
        upper: float = 0.95,
    ):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"threshold phải trong [0,1], nhận {threshold}")
        if not 0.0 <= lower < upper <= 1.0:
            raise ValueError(f"Cần 0 <= lower < upper <= 1, nhận lower={lower}, upper={upper}")

        self.threshold = threshold
        self.lower = lower
        self.upper = upper
        self.model = joblib.load(model_path)

    @staticmethod
    def extract_blank_features(image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 1. Black pixel ratio (Ngưỡng 127)
        black_ratio = float(np.sum(gray < 127) / gray.size)

        # 2. Standard Deviation
        std_val = float(np.std(gray))

        # 3. Entropy
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten() / gray.size
        hist = hist[hist > 0]
        entropy_val = float(-np.sum(hist * np.log2(hist)))

        return np.array([[black_ratio, std_val, entropy_val]])

    def is_blank(self, image: np.ndarray) -> Tuple[bool, float, str]:
        features = self.extract_blank_features(image)
        black_ratio = float(features[0])

        # Fast path: vùng chắc chắn
        if black_ratio < self.lower:
            return True, 1.0, f"density_too_white (ratio={black_ratio:.4f})"
        if black_ratio > self.upper:
            return True, 1.0, f"density_too_black (ratio={black_ratio:.4f})"

        probs = self.model.predict_proba(features.reshape(1, -1))[0]
        blank_score = float(probs[1])
        is_blank = blank_score >= self.threshold

        return is_blank, blank_score, f"rf_model (score={blank_score:.4f})"