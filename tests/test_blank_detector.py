import pytest
import numpy as np
from strategies.preprocessor import BlankDetector

@pytest.fixture
def detector():
    # Thay đường dẫn model thực tế của bạn vào đây
    return BlankDetector(model_path="models/rf_blank_classifier.joblib")

def test_pure_white_page(detector):
    """Test trang trắng tinh tuyệt đối."""
    img = np.ones((1000, 1000), dtype=np.uint8) * 255
    is_blank, score, reason = detector.is_blank(img)
    assert is_blank is True
    assert score == 1.0
    assert "too_white" in reason

def test_pure_black_page(detector):
    """Test trang đen xì (lỗi scan)."""
    img = np.zeros((1000, 1000), dtype=np.uint8)
    is_blank, score, reason = detector.is_blank(img)
    assert is_blank is True
    assert score == 1.0
    assert "too_black" in reason

def test_content_page(detector):
    """Test trang có chữ (giả lập bằng vạch đen)."""
    img = np.ones((1000, 1000), dtype=np.uint8) * 255
    img[100:200, :] = 0 
    is_blank, score, reason = detector.is_blank(img)
    assert is_blank is False
    assert score < 0.5