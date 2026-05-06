import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ocr.schema import WordResult, OCRResult
from ocr.confidence import ConfidenceScorer

# ====================================================================
# DUMMY DATA
# --------------------------------------------------------------------
dummy_result = OCRResult(
    words=[
        WordResult(text="Quyết",  confidence=0.95, x=10,  y=10, width=50, height=20),
        WordResult(text="định",   confidence=0.91, x=65,  y=10, width=40, height=20),
        WordResult(text="số",     confidence=0.55, x=110, y=10, width=20, height=20),
        WordResult(text="123/QĐ", confidence=0.42, x=135, y=10, width=60, height=20),
        WordResult(text="UBND",   confidence=0.88, x=200, y=10, width=50, height=20),
    ]
)

# ====================================================================
# TEST
# --------------------------------------------------------------------
scorer = ConfidenceScorer(threshold=0.8)
result = scorer.score(dummy_result)

print(result)
print()
print("SUMMARY:", scorer.summary(result))

# ====================================================================
# ASSERT — tự động kiểm tra kết quả đúng/sai
# --------------------------------------------------------------------
assert result.words[0].flagged == False, "Quyết không được flag"
assert result.words[1].flagged == False, "định không được flag"
assert result.words[2].flagged == True,  "số phải bị flag"
assert result.words[3].flagged == True,  "123/QĐ phải bị flag"
assert result.words[4].flagged == False, "UBND không được flag"
assert len(scorer.get_flagged(result)) == 2, "Phải có đúng 2 từ bị flag"
assert round(result.overall_confidence, 3) == 0.742, "overall_confidence phải là 0.742"

print("\n Tất cả test đều pass!")