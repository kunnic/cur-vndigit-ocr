"""
scoring.py — Chấm điểm độ tin cậy (confidence) cho từng field trích xuất.

Tách ra từ notebook để:
  - Dễ unit-test độc lập với LLM.
  - Dễ tuning rule per-schema mà không đụng vào extractor.
  - Dễ mở rộng thêm rule mới (regex, cross-validate, business logic).

Export chính:
  compute_field_confidence(value, field_name) → float
  score_extraction(extracted_dict, schema_class, threshold) → (metadata_list, overall, fill_rate)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel


# ══════════════════════════════════════════════════════════════════════════════
# PATTERN LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
_RE_SO_HIEU   = re.compile(r"^\d{1,3}/\d{4}/[A-Z]{2,}(-[A-Z]+)?$")
_RE_DATE_VN   = re.compile(r"\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4}")
_RE_DATE_TXT  = re.compile(r"\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}", re.IGNORECASE)
_RE_CCCD      = re.compile(r"^\d{9}$|^\d{12}$")
_RE_DIGIT     = re.compile(r"\d")

# Số sổ BHXH: 10 chữ số
_RE_BHXH_SO_SO = re.compile(r"^\d{10}$")
# Số thẻ BHYT: bắt đầu bằng 2 chữ cái + 13 chữ số, hoặc 15 ký tự
_RE_BHYT_THE   = re.compile(r"^[A-Z]{2}\d{13}$|^[A-Z]{2}\d{11}[A-Z0-9]{2}$")
# Mã số thuế: 10 hoặc 13 chữ số
_RE_MST        = re.compile(r"^\d{10}(-\d{3})?$")

# Field groups — dùng để dispatch rule
_GROUP_SO_HIEU   = ("so_hieu", "so_ban_an", "thu_ly", "so_hop_dong",
                    "so_quyet_dinh", "so_so_bhxh", "ma_so_bhxh")
_GROUP_NGAY      = ("ngay", "ngày", "date", "ngay_sinh", "ngay_ky",
                    "ngay_cap", "ngay_het_han", "ngay_hieu_luc")
_GROUP_NAME      = ("ho_ten", "ten_nguoi", "tham_phan", "thu_ky", "kiem_sat",
                    "ten_bi", "nguyen_don", "bi_don", "nguoi_", "ben_a", "ben_b",
                    "ten_bi_can", "nguoi_viet", "nguoi_chu_tri", "nguoi_tham_gia")
_GROUP_ORG       = ("toa_an", "co_quan", "don_vi", "co_so", "noi_cap",
                    "noi_nhan")
_GROUP_CONTENT   = ("loai", "toi_danh", "vu_viec", "noi_dung", "doi_tuong",
                    "dieu_khoan", "bien_phap", "quyet_dinh_ban_an", "muc_huong",
                    "gia_tri", "thoi_han", "thoi_gian", "muc_luong")
_GROUP_BHXH_THE  = ("so_the_bhyt",)
_GROUP_CCCD      = ("cccd", "cmnd", "so_giay_to")
_GROUP_MST       = ("ma_so_thue",)


def _match_group(fname: str, group: tuple) -> bool:
    f = fname.lower()
    return any(k in f for k in group)


# ══════════════════════════════════════════════════════════════════════════════
# CORE: compute_field_confidence
# ══════════════════════════════════════════════════════════════════════════════
def compute_field_confidence(value: Any, field_name: str) -> float:
    """
    Tính điểm tin cậy [0.0, 1.0] cho 1 field dựa trên format của value.

    Rule-based, không cần LLM. Mỗi "group" field có rule riêng.
    Trả 0.0 nếu value là None / chuỗi rỗng.
    """
    if value is None or str(value).strip() == "":
        return 0.0

    v = str(value).strip()
    f = field_name.lower()

    # ── Số hiệu văn bản ──────────────────────────────────────────────────────
    if _match_group(f, _GROUP_SO_HIEU):
        # Ưu tiên check BHXH trước (10 số)
        if "bhxh" in f or "so_so" in f:
            return 0.95 if _RE_BHXH_SO_SO.match(v.replace(" ", "")) else (
                0.70 if _RE_DIGIT.search(v) else 0.40
            )
        return 0.95 if _RE_SO_HIEU.match(v) else (
            0.72 if _RE_DIGIT.search(v) else 0.45
        )

    # ── Số thẻ BHYT ──────────────────────────────────────────────────────────
    if _match_group(f, _GROUP_BHXH_THE):
        clean = v.replace(" ", "").upper()
        return 0.95 if _RE_BHYT_THE.match(clean) else (
            0.65 if (len(clean) >= 10 and _RE_DIGIT.search(clean)) else 0.35
        )

    # ── CCCD / CMND ──────────────────────────────────────────────────────────
    if _match_group(f, _GROUP_CCCD):
        clean = v.replace(" ", "")
        return 0.95 if _RE_CCCD.match(clean) else (
            0.65 if _RE_DIGIT.search(clean) else 0.35
        )

    # ── Mã số thuế ───────────────────────────────────────────────────────────
    if _match_group(f, _GROUP_MST):
        clean = v.replace(" ", "")
        return 0.95 if _RE_MST.match(clean) else (
            0.65 if _RE_DIGIT.search(clean) else 0.35
        )

    # ── Ngày tháng ───────────────────────────────────────────────────────────
    if _match_group(f, _GROUP_NGAY):
        if _RE_DATE_VN.search(v) or _RE_DATE_TXT.search(v):
            return 0.95
        if _RE_DIGIT.search(v):
            return 0.55
        return 0.30

    # ── Năm sinh đơn lẻ ──────────────────────────────────────────────────────
    if any(k in f for k in ("nam_sinh", "year")):
        try:
            return 0.95 if 1900 <= int(v) <= 2030 else 0.50
        except ValueError:
            return 0.30

    # ── Họ tên người ─────────────────────────────────────────────────────────
    if _match_group(f, _GROUP_NAME):
        if ";" in v:
            parts = [p.strip() for p in v.split(";") if p.strip()]
            ok = sum(1 for p in parts if len(p.split()) >= 2)
            return round(min(0.70 + 0.08 * ok, 0.95), 2)
        # Tên người thường >= 2 từ, không chứa số
        return 0.88 if (len(v.split()) >= 2 and not _RE_DIGIT.search(v)) else 0.70

    # ── Tên cơ quan / tổ chức ────────────────────────────────────────────────
    if _match_group(f, _GROUP_ORG):
        return 0.85 if len(v.split()) >= 3 else 0.70

    # ── Nội dung / mô tả dài ─────────────────────────────────────────────────
    if _match_group(f, _GROUP_CONTENT):
        if len(v) >= 30:
            return 0.85
        if len(v.split()) >= 3:
            return 0.75
        return 0.60

    # ── Default ───────────────────────────────────────────────────────────────
    return 0.78 if len(v.split()) >= 2 else 0.60


# ══════════════════════════════════════════════════════════════════════════════
# CORE: score_extraction
# ══════════════════════════════════════════════════════════════════════════════
def score_extraction(
    extracted: Dict[str, Any],
    schema_class: Type[BaseModel],
    low_conf_threshold: float = 0.65,
) -> Tuple[List[dict], float, float]:
    """
    Chấm điểm toàn bộ kết quả trích xuất của 1 document.

    Args:
        extracted:          dict {field_name: value} từ LLM output.
        schema_class:       Pydantic schema tương ứng.
        low_conf_threshold: Ngưỡng để flag field cần QA review.

    Returns:
        metadata_list : list[dict] theo chuẩn API Contract.
                        Mỗi phần tử có: field_name, value, confidence,
                        flagged, missing (và tùy chọn: warning).
        overall_conf  : float — trung bình confidence trên field CÓ dữ liệu.
        fill_rate     : float — tỷ lệ field có dữ liệu / tổng field.
    """
    metadata_list: List[dict] = []
    confs: List[float] = []

    props = schema_class.model_json_schema().get("properties", {})

    for fname in props:
        val    = extracted.get(fname)
        conf   = compute_field_confidence(val, fname)
        is_null = val is None or str(val).strip() == ""

        entry: dict = {
            "field_name": fname,
            "value":      val,
            "confidence": round(conf, 3) if not is_null else None,
            "flagged":    False if is_null else (conf < low_conf_threshold),
            "missing":    is_null,
        }
        metadata_list.append(entry)
        if not is_null:
            confs.append(conf)

    # ── Cross-validate: năm trong so_hieu ↔ ngay_ban_hanh ────────────────────
    _cross_validate_year(metadata_list)

    # ── Thống kê ──────────────────────────────────────────────────────────────
    total     = len(metadata_list)
    filled    = sum(1 for m in metadata_list if not m["missing"])
    fill_rate = round(filled / total, 3) if total else 0.0
    overall   = round(sum(confs) / len(confs), 3) if confs else 0.0

    return metadata_list, overall, fill_rate


# ══════════════════════════════════════════════════════════════════════════════
# CROSS-VALIDATION RULES
# ══════════════════════════════════════════════════════════════════════════════
def _cross_validate_year(metadata_list: List[dict]) -> None:
    """
    Rule: năm trong `so_hieu` phải khớp với năm trong `ngay_ban_hanh`.
    Nếu không khớp → giảm confidence 30% và đặt warning.
    Mutate in-place.
    """
    sh = next((m for m in metadata_list if m["field_name"] == "so_hieu"), None)
    nb = next((m for m in metadata_list if m["field_name"] in ("ngay_ban_hanh", "ngay_ky")), None)

    if not (sh and nb and sh["value"] and nb["value"]):
        return

    m1 = re.search(r"/(\d{4})/", str(sh["value"]))
    m2 = re.search(r"(\d{4})", str(nb["value"]))
    if m1 and m2 and m1.group(1) != m2.group(1):
        for entry in (sh, nb):
            if entry["confidence"] is not None:
                entry["confidence"] = round(entry["confidence"] * 0.7, 3)
                entry["flagged"]    = True
                entry["warning"]    = (
                    f"Năm không khớp: so_hieu={m1.group(1)} "
                    f"↔ ngay={m2.group(1)}"
                )


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY HELPER (dùng cho logging / thống kê pipeline)
# ══════════════════════════════════════════════════════════════════════════════
def summarize_results(results: List[dict]) -> dict:
    """
    Tổng hợp thống kê sau khi chạy pipeline.

    Args:
        results: list[dict] API Contract từ GeminiExtractor.

    Returns dict gồm:
        total, success_count, error_count,
        avg_confidence, avg_fill_rate,
        high_conf / med_conf / low_conf counts,
        schema_distribution: {schema_name: count},
        flagged_fields: list[dict] — các field bị flag (để review).
    """
    from collections import Counter

    success = [r for r in results if not r.get("error")]
    errors  = [r for r in results if  r.get("error")]
    n_total = len(results)
    n_ok    = len(success)

    avg_conf = (
        sum(r["confidence_overall"] for r in success) / n_ok if n_ok else 0.0
    )
    avg_fill = (
        sum(r.get("fill_rate", 0) for r in success) / n_ok if n_ok else 0.0
    )

    high_conf = sum(1 for r in success if r["confidence_overall"] >= 0.80)
    med_conf  = sum(1 for r in success if 0.65 <= r["confidence_overall"] < 0.80)
    low_conf  = sum(1 for r in success if r["confidence_overall"] < 0.65)

    schema_dist = Counter(r.get("classification", "UNKNOWN") for r in results)

    flagged: List[dict] = []
    for r in results:
        for m in r.get("metadata", []):
            if m.get("flagged"):
                flagged.append({
                    "document_id": r.get("document_id"),
                    "field_name":  m["field_name"],
                    "value":       m.get("value"),
                    "confidence":  m.get("confidence"),
                    "warning":     m.get("warning", ""),
                })

    return {
        "total":             n_total,
        "success_count":     n_ok,
        "error_count":       len(errors),
        "avg_confidence":    round(avg_conf, 3),
        "avg_fill_rate":     round(avg_fill, 3),
        "high_conf_count":   high_conf,
        "med_conf_count":    med_conf,
        "low_conf_count":    low_conf,
        "schema_distribution": dict(schema_dist),
        "flagged_fields":    flagged,
    }