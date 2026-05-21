# import sys
# from pathlib import Path

# root_dir = Path(__file__).resolve().parent.parent
# sys.path.insert(0, str(root_dir))

# from src.correction.autocorrect import AutoCorrector

# if __name__ == "__main__":
#     config = {
#         "enabled": True,
#         "min_confidence": 0.7
#     }
    
#     corrector = AutoCorrector(config)
    
#     test_cases = [
#         "So l1 la van ban so 123/BC-UBND",
#         "Ngay 0l/05/2O24, tai TP. Ho Chi Minh",
#         "Co quan ban hanh: UBND Thanh pho",
#         "Dia chi: 12 l0 Nguyen Hue",
#         "Thoi gian: 0l:3O",
#         "a hanh chinh"
#     ]

#     confidences = [
#     0.95,
#     0.45,
#     0.52,
#     0.91,
#     0.40,
#     0.98
#     ]
    
#     print("Trước sửa:", test_cases)
#     print("-" * 70)
    
#     result = corrector.correct_list(test_cases, confidences)
    
#     print("Sau sửa :", result.corrected_texts)
#     print(f"Tổng số lỗi đã sửa: {result.corrected_count}\n")
    
#     if result.corrections:
#         for corr in result.corrections:
#             print(f"   ✓ {corr.original_text:35} → {corr.corrected_text}  ({corr.reason})")
#     else:
#         print("Không có từ nào được sửa.")

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
from src.correction.autocorrect import AutoCorrector

if __name__ == "__main__":

    config = {
        "enabled": True,
        "min_confidence": 0.8
    }

    corrector = AutoCorrector(config)

    test_cases = [
        # Rule-based OCR errors
        "So l1 la van ban so 123/BC-UBND",
        "Ngay 0l/05/2O24 tai TP Ho Chi Minh",
        "Dia chi 12 l0 Nguyen Hue",
        "Thoi gian 0l:3O",

        # Bigram contextual correction
        "Can cu vao hop dong lao dong",
        "Uy ban nhan dan thanh pho",

        # False positive check
        "Ngay hop mat",
        "Dia diem hop",
        "Thoi tiet dep"
    ]

    confidences = [

        0.95,   # skip dictionary
        0.45,   # apply correction
        0.52,
        0.40,
        0.35,
        0.38,
        0.90,   # should skip
        0.92,
        0.96

    ]

    result = corrector.correct_list(
        test_cases,
        confidences
    )

    print(
        f"\nTotal corrections: "
        f"{result.corrected_count}\n"
    )

    if result.corrections:

        for corr in result.corrections:

            print(
                f"✓ "
                f"{corr.original_text}"
                f" -> "
                f"{corr.corrected_text} "
                f"({corr.reason})"
            )

    else:
        print("Không có correction nào.")