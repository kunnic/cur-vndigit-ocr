from .adapter import OCRAdapter
from .base import BaseOCR
from .confidence import normalize_confidence
from .models import AdaptedOCRResult, OCRResult, TextBlock, WordResult
from .paddle import PaddleConfig, PaddleOCRModel, PaddleTextRecognizer
from .tesseract import TesseractConfig, TesseractOCR

__all__ = [
    "AdaptedOCRResult",
    "BaseOCR",
    "normalize_confidence",
    "OCRAdapter",
    "OCRResult",
    "PaddleConfig",
    "PaddleOCRModel",
    "PaddleTextRecognizer",
    "TextBlock",
    "TesseractConfig",
    "TesseractOCR",
    "WordResult",
]
