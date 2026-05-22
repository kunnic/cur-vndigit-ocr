# import sys
# from pathlib import Path
# root_dir = Path(__file__).resolve().parent.parent
# sys.path.insert(0, str(root_dir))
# from src.correction.autocorrect import AutoCorrector

# if __name__ == "__main__":

#     config = {
#         "enabled": True,
#         "min_confidence": 0.8
#     }

#     corrector = AutoCorrector(config)

#     test_cases = [
#         # Rule-based OCR errors
#         "So l1 la van ban so 123/BC-UBND",
#         "Ngay 0l/05/2O24 tai TP Ho Chi Minh",
#         "Dia chi 12 l0 Nguyen Hue",
#         "Thoi gian 0l:3O",

#         # Bigram contextual correction
#         "Can cu vao hop dong lao dong",
#         "Uy ban nhan dan thanh pho",

#         # False positive check
#         "Ngay hop mat",
#         "Dia diem hop",
#         "Thoi tiet dep"
#     ]

#     confidences = [

#         0.95,   # skip dictionary
#         0.45,   # apply correction
#         0.52,
#         0.40,
#         0.35,
#         0.38,
#         0.90,   # should skip
#         0.92,
#         0.96

#     ]

#     result = corrector.correct_list(
#         test_cases,
#         confidences
#     )

#     print(
#         f"\nTotal corrections: "
#         f"{result.corrected_count}\n"
#     )

#     if result.corrections:

#         for corr in result.corrections:

#             print(
#                 f"✓ "
#                 f"{corr.original_text}"
#                 f" -> "
#                 f"{corr.corrected_text} "
#                 f"({corr.reason})"
#             )

#     else:
#         print("Không có correction nào.")

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

        # =========================
        # RULE-BASED OCR ERRORS
        # =========================

        "So 0l/QD-UBND",
        "Ngay 2O/05/2O24",
        "Thoi gian 0l:3O",
        "Dia chi 12 l0 Nguyen Hue",

        # =========================
        # CONTEXTUAL BIGRAM TEST
        # =========================

        "Can cu vao hop dong lao dong",

        "Uy ban nhan dan thanh pho",

        "Dia chi lien he",

        "Thoi gian thuc hien",

        "Cong hoa xa hoi chu nghia Viet Nam",

        # =========================
        # FALSE POSITIVE TEST
        # =========================

        "Ngay hop mat cuoi nam",

        "Dia diem hop lop",

        "Thoi tiet hom nay dep",

        "Can ban nha mat tien",

        "Nhan vien hanh chinh",

        # =========================
        # OCR NOISE TEST
        # =========================

        "Hop d0ng lao d0ng",

        "Uy ban nhan d4n",

        "Thoi gi4n lam viec",

        "Dja chi lien he",

        # =========================
        # HARD CASES
        # =========================

        "Thong bao tuyen dung",

        "Quyet dinh so 12/QD-UBND",

        "Can cu theo quy dinh hien hanh",

        "Ngay 0l thang 05 nam 2O24"

    ]

    confidences = [

        # Rule-based
        0.40,
        0.35,
        0.30,
        0.42,

        # Contextual
        0.45,
        0.50,
        0.48,
        0.52,
        0.43,

        # False positive
        0.95,
        0.96,
        0.97,
        0.94,
        0.98,

        # OCR noise
        0.38,
        0.41,
        0.36,
        0.39,

        # Hard cases
        0.60,
        0.55,
        0.58,
        0.37
    ]

    print("\n=== BEFORE CORRECTION ===\n")

    for text in test_cases:
        print(text)

    print("\n" + "=" * 70)

    result = corrector.correct_list(
        test_cases,
        confidences
    )

    print("\n=== AFTER CORRECTION ===\n")

    for text in result.corrected_texts:
        print(text)

    print("\n" + "=" * 70)

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