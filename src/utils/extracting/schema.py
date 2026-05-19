"""
schema.py — Pydantic schemas cho từng loại văn bản pháp lý / chuyên ngành.

Cấu trúc:
  - Mỗi "khối" nghiệp vụ định nghĩa 1 Pydantic BaseModel.
  - SCHEMA_REGISTRY: dict[tên_schema → class] — registry trung tâm.
  - SCHEMA_KEYWORDS: danh sách keyword để auto-detect loại văn bản.
  - auto_detect_schema(text) → (tên_schema, class)
  - register_schema(...)    → đăng ký schema tùy chỉnh từ ngoài (dynamic).
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Dict, Type, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# KHỐI TÒA ÁN
# ══════════════════════════════════════════════════════════════════════════════
class VanBanToaAnSchema(BaseModel):
    """Bản án, Quyết định xét xử, Quyết định đình chỉ của Tòa án."""
    loai_van_ban:               Optional[str] = Field(default=None, description="VD: Bản án sơ thẩm, Quyết định công nhận thuận tình ly hôn")
    so_hieu:                    Optional[str] = Field(default=None, description="VD: 03/2022/DSST, 89/2026/QĐST-HNGĐ")
    ngay_ban_hanh:              Optional[str] = Field(default=None, description="VD: 23/11/2022")
    ten_toa_an:                 Optional[str] = Field(default=None, description="VD: Tòa án nhân dân tỉnh BN")
    vu_viec_tom_tat:            Optional[str] = Field(default=None, description="Tóm tắt nội dung vụ việc / tội danh")
    tham_phan_chu_toa:          Optional[str] = Field(default=None, description="Tên Thẩm phán hoặc Chủ tọa")
    nguyen_don_nguoi_khoi_kien: Optional[str] = Field(default=None, description="Tên Nguyên đơn / Người khởi kiện / Người yêu cầu")
    bi_don_nguoi_bi_kien:       Optional[str] = Field(default=None, description="Tên Bị đơn / Người bị kiện / Bị cáo")
    quyet_dinh_ban_an:          Optional[str] = Field(default=None, description="Tóm tắt phần quyết định (hình phạt, bồi thường, ...)")


# ══════════════════════════════════════════════════════════════════════════════
# KHỐI ĐIỀU TRA (Công an / Viện Kiểm sát)
# ══════════════════════════════════════════════════════════════════════════════
class VanBanDieuTraSchema(BaseModel):
    """Kết luận điều tra, Lệnh bắt, Lệnh cấm đi khỏi, Quyết định khởi tố."""
    loai_van_ban:        Optional[str] = Field(default=None, description="VD: Bản kết luận điều tra, Lệnh cấm đi khỏi nơi cư trú")
    so_hieu:             Optional[str] = Field(default=None, description="VD: 65/KLĐT-PC03")
    ngay_ban_hanh:       Optional[str] = Field(default=None, description="VD: 03 tháng 11 năm 2021")
    co_quan_ban_hanh:    Optional[str] = Field(default=None, description="VD: Cơ quan Cảnh sát điều tra Công an tỉnh Quảng Bình")
    ten_bi_can_doi_tuong:Optional[str] = Field(default=None, description="Họ tên bị can / đối tượng bị điều tra")
    toi_danh_vu_an:      Optional[str] = Field(default=None, description="Tội danh hoặc tên vụ án")
    bien_phap_ngan_chan: Optional[str] = Field(default=None, description="VD: Tạm giam, Cấm đi khỏi nơi cư trú, Bảo lĩnh")


# ══════════════════════════════════════════════════════════════════════════════
# KHỐI HÀNH CHÍNH (UBND / Sở / Ban ngành)
# ══════════════════════════════════════════════════════════════════════════════
class VanBanHanhChinhSchema(BaseModel):
    """Quyết định hành chính, Thông báo, Kết luận thanh tra của cơ quan nhà nước."""
    loai_van_ban:    Optional[str] = Field(default=None, description="VD: Quyết định, Thông báo, Kết luận thanh tra")
    so_hieu:         Optional[str] = Field(default=None, description="VD: 1059/QĐ-UBND")
    ngay_ban_hanh:   Optional[str] = Field(default=None, description="VD: 29 tháng 3 năm 2021")
    co_quan_ban_hanh:Optional[str] = Field(default=None, description="VD: UBND thành phố Đà Lạt")
    noi_dung_tom_tat:Optional[str] = Field(default=None, description="Về việc gì")
    nguoi_ky:        Optional[str] = Field(default=None, description="Tên người ký văn bản")
    chuc_vu_nguoi_ky:Optional[str] = Field(default=None, description="VD: Chủ tịch UBND, Giám đốc Sở")


# ══════════════════════════════════════════════════════════════════════════════
# BIÊN BẢN (lời khai, vi phạm hành chính, đối chất, ...)
# ══════════════════════════════════════════════════════════════════════════════
class BienBanSchema(BaseModel):
    """Biên bản ghi lời khai, vi phạm hành chính, đối chất, giao nhận."""
    ten_bien_ban:            Optional[str] = Field(default=None, description="VD: Biên bản ghi lời khai, vi phạm hành chính")
    thoi_gian_lap:           Optional[str] = Field(default=None, description="Thời gian lập biên bản")
    dia_diem_lap:            Optional[str] = Field(default=None, description="Nơi lập biên bản")
    nguoi_chu_tri_lap:       Optional[str] = Field(default=None, description="Tên cán bộ / người lập")
    nguoi_tham_gia_doi_tuong:Optional[str] = Field(default=None, description="Tên người được lấy lời khai / bị lập biên bản")
    noi_dung_chinh:          Optional[str] = Field(default=None, description="Tóm tắt nội dung biên bản")


# ══════════════════════════════════════════════════════════════════════════════
# ĐƠN TỪ / CAM KẾT / XÁC NHẬN
# ══════════════════════════════════════════════════════════════════════════════
class DonTuCamKetSchema(BaseModel):
    """Đơn tố cáo, khiếu nại, Bản cam kết, Giấy xác nhận do cá nhân lập."""
    loai_giay_to:               Optional[str] = Field(default=None, description="VD: Đơn tố cáo, Bản cam kết, Giấy xác nhận")
    nguoi_viet_don_cam_ket:     Optional[str] = Field(default=None, description="Tên người đứng đơn")
    noi_nhan_co_quan_giai_quyet:Optional[str] = Field(default=None, description="Kính gửi ai / cơ quan nào")
    ngay_thang_nam:             Optional[str] = Field(default=None, description="Ngày tháng ghi trên đơn")
    noi_dung_tom_tat:           Optional[str] = Field(default=None, description="Tóm tắt nội dung")


# ══════════════════════════════════════════════════════════════════════════════
# KHỐI BẢO HIỂM XÃ HỘI (BHXH / BHYT / BHTN)
# ══════════════════════════════════════════════════════════════════════════════
class BaoHiemSchema(BaseModel):
    """
    Hồ sơ / quyết định / phiếu liên quan đến Bảo hiểm Xã hội, Y tế, Thất nghiệp.
    Ví dụ: Quyết định hưởng lương hưu, Phiếu xác nhận BHYT, Sổ BHXH.
    """
    loai_van_ban:      Optional[str] = Field(default=None, description="VD: Sổ BHXH, Quyết định hưởng lương hưu, Phiếu xác nhận BHYT")
    so_so_bhxh:        Optional[str] = Field(default=None, description="Số sổ BHXH (10 chữ số)")
    ma_so_bhxh:        Optional[str] = Field(default=None, description="Mã số BHXH (nếu khác số sổ)")
    so_the_bhyt:       Optional[str] = Field(default=None, description="Số thẻ BHYT (VD: GD4100123456789)")
    ten_nguoi_tham_gia:Optional[str] = Field(default=None, description="Họ tên người tham gia bảo hiểm")
    ngay_sinh:         Optional[str] = Field(default=None, description="Ngày sinh người tham gia")
    don_vi_tham_gia:   Optional[str] = Field(default=None, description="Tên đơn vị / doanh nghiệp đóng BHXH")
    ma_so_thue_don_vi: Optional[str] = Field(default=None, description="Mã số thuế đơn vị tham gia (nếu có)")
    thoi_gian_dong:    Optional[str] = Field(default=None, description="Số tháng / số năm đã đóng BHXH")
    muc_luong_dong:    Optional[str] = Field(default=None, description="Mức tiền lương / thu nhập đóng BHXH")
    co_so_kham_chua:   Optional[str] = Field(default=None, description="Cơ sở KCB ban đầu đăng ký trên thẻ BHYT")
    ngay_hieu_luc:     Optional[str] = Field(default=None, description="Ngày hiệu lực / ngày hết hạn của thẻ BHYT")
    so_quyet_dinh:     Optional[str] = Field(default=None, description="Số quyết định hưởng chế độ (hưu trí, trợ cấp, ...)")
    muc_huong:         Optional[str] = Field(default=None, description="Mức lương hưu / trợ cấp hàng tháng (nếu có)")


# ══════════════════════════════════════════════════════════════════════════════
# KHỐI HỢP ĐỒNG (dân sự, lao động, kinh tế)
# ══════════════════════════════════════════════════════════════════════════════
class HopDongSchema(BaseModel):
    """
    Hợp đồng dân sự, lao động, kinh tế, chuyển nhượng, thuê mướn.
    """
    loai_hop_dong:   Optional[str] = Field(default=None, description="VD: Hợp đồng lao động, Hợp đồng mua bán, Hợp đồng thuê nhà")
    so_hop_dong:     Optional[str] = Field(default=None, description="Số / ký hiệu hợp đồng")
    ngay_ky:         Optional[str] = Field(default=None, description="Ngày ký hợp đồng")
    ben_a:           Optional[str] = Field(default=None, description="Tên và thông tin Bên A (bên thuê / mua / sử dụng lao động)")
    ben_b:           Optional[str] = Field(default=None, description="Tên và thông tin Bên B (bên cho thuê / bán / người lao động)")
    doi_tuong_hop_dong:Optional[str] = Field(default=None, description="Đối tượng / nội dung chính của hợp đồng")
    gia_tri_hop_dong:Optional[str] = Field(default=None, description="Giá trị, số tiền, mức lương thỏa thuận")
    thoi_han_hop_dong:Optional[str] = Field(default=None, description="Thời hạn hiệu lực hợp đồng")
    dieu_khoan_phat: Optional[str] = Field(default=None, description="Điều khoản phạt vi phạm / chấm dứt hợp đồng (nếu có)")


# ══════════════════════════════════════════════════════════════════════════════
# KHỐI GIẤY TỜ NHÂN THÂN (CCCD, CMND, Hộ khẩu, Giấy khai sinh)
# ══════════════════════════════════════════════════════════════════════════════
class GiayToNhanThanSchema(BaseModel):
    """
    Căn cước công dân, CMND, Hộ chiếu, Hộ khẩu, Giấy khai sinh.
    """
    loai_giay_to:    Optional[str] = Field(default=None, description="VD: CCCD, CMND, Hộ chiếu, Giấy khai sinh")
    so_giay_to:      Optional[str] = Field(default=None, description="Số CCCD / CMND / Hộ chiếu / Khai sinh")
    ho_ten:          Optional[str] = Field(default=None, description="Họ và tên người được cấp")
    ngay_sinh:       Optional[str] = Field(default=None, description="Ngày tháng năm sinh")
    gioi_tinh:       Optional[str] = Field(default=None, description="Nam / Nữ")
    que_quan:        Optional[str] = Field(default=None, description="Quê quán (tỉnh / huyện / xã)")
    thuong_tru:      Optional[str] = Field(default=None, description="Nơi thường trú")
    ngay_cap:        Optional[str] = Field(default=None, description="Ngày cấp giấy tờ")
    noi_cap:         Optional[str] = Field(default=None, description="Cơ quan cấp (VD: Cục Cảnh sát QLHC về TTXH)")
    ngay_het_han:    Optional[str] = Field(default=None, description="Ngày hết hạn (nếu có)")
    dan_toc:         Optional[str] = Field(default=None, description="Dân tộc (nếu có trên giấy tờ)")


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY TRUNG TÂM
# ══════════════════════════════════════════════════════════════════════════════
SCHEMA_REGISTRY: Dict[str, Type[BaseModel]] = {
    "VAN_BAN_TOA_AN":        VanBanToaAnSchema,
    "VAN_BAN_DIEU_TRA":      VanBanDieuTraSchema,
    "QUYET_DINH_HANH_CHINH": VanBanHanhChinhSchema,
    "BIEN_BAN":              BienBanSchema,
    "DON_TU_CAM_KET":        DonTuCamKetSchema,
    "BAO_HIEM":              BaoHiemSchema,
    "HOP_DONG":              HopDongSchema,
    "GIAY_TO_NHAN_THAN":     GiayToNhanThanSchema,
}

# Keyword map — thứ tự quan trọng: specific trước, generic sau
SCHEMA_KEYWORDS: List[Tuple[str, List[str]]] = [
    ("VAN_BAN_TOA_AN",        ["tòa án nhân dân", "bản án số", "quyết định đình chỉ xét xử",
                                "tòa phúc thẩm", "hội đồng xét xử", "thẩm phán", "xét xử",
                                "bị cáo", "nguyên đơn", "bị đơn", "viện kiểm sát nhân dân"]),
    ("VAN_BAN_DIEU_TRA",      ["kết luận điều tra", "cơ quan cảnh sát điều tra",
                                "khởi tố bị can", "lệnh cấm đi khỏi", "truy tố",
                                "lệnh bắt", "quyết định khởi tố", "tạm giam"]),
    ("BAO_HIEM",              ["số sổ bhxh", "mã số bhxh", "bảo hiểm xã hội",
                                "bảo hiểm y tế", "số thẻ bhyt", "lương hưu",
                                "trợ cấp thất nghiệp", "bhxh", "bhyt", "bhtn",
                                "cơ sở khám chữa bệnh ban đầu"]),
    ("HOP_DONG",              ["hợp đồng lao động", "hợp đồng mua bán", "hợp đồng thuê",
                                "hợp đồng dịch vụ", "hợp đồng chuyển nhượng",
                                "bên a", "bên b", "điều khoản", "hợp đồng số"]),
    ("GIAY_TO_NHAN_THAN",     ["căn cước công dân", "chứng minh nhân dân", "hộ chiếu",
                                "giấy khai sinh", "sổ hộ khẩu", "cccd", "cmnd",
                                "nơi thường trú", "quê quán"]),
    ("BIEN_BAN",              ["biên bản vi phạm", "biên bản ghi lời khai",
                                "biên bản đối chất", "biên bản thỏa thuận",
                                "biên bản giao nhận", "biên bản làm việc"]),
    ("QUYET_DINH_HANH_CHINH", ["quyết định", "ủy ban nhân dân", "ubnd",
                                "thanh tra tỉnh", "thu hồi", "sở tài nguyên",
                                "đình chỉ công tác", "xử phạt vi phạm hành chính"]),
    ("DON_TU_CAM_KET",        ["đơn tố cáo", "bản cam kết", "giấy cam kết",
                                "thư cảm ơn", "giấy xác nhận", "đơn khiếu nại",
                                "tôi tên là", "đơn đề nghị"]),
]


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-DETECT
# ══════════════════════════════════════════════════════════════════════════════
def auto_detect_schema(text: str) -> Tuple[str, Type[BaseModel]]:
    """
    Dò keyword trong text (không phân biệt hoa thường) để chọn schema phù hợp.
    Fallback: DON_TU_CAM_KET.
    """
    t = text.lower()
    for name, keywords in SCHEMA_KEYWORDS:
        if any(kw in t for kw in keywords):
            return name, SCHEMA_REGISTRY[name]
    return "DON_TU_CAM_KET", SCHEMA_REGISTRY["DON_TU_CAM_KET"]


# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC REGISTRATION — Admin / plugin có thể đăng ký schema mới lúc runtime
# ══════════════════════════════════════════════════════════════════════════════
def register_schema(
    name: str,
    schema_class: Type[BaseModel],
    keywords: List[str],
    priority: int = 0,
) -> None:
    """
    Đăng ký schema tùy chỉnh vào registry. Không cần sửa file này.

    Args:
        name:         Tên định danh duy nhất (VD: "BHXH_LONG_AN").
        schema_class: Pydantic BaseModel class.
        keywords:     List keyword để auto-detect (tiếng Việt thường).
        priority:     0 = chèn cuối, 1 = chèn trước generic schemas,
                      2 = chèn đầu danh sách (ưu tiên cao nhất).

    Ví dụ:
        from pydantic import BaseModel, Field
        from schema import register_schema

        class BhxhLongAnSchema(BaseModel):
            so_so_bhxh: Optional[str] = Field(...)
            ma_don_vi:  Optional[str] = Field(...)

        register_schema(
            name="BHXH_LONG_AN",
            schema_class=BhxhLongAnSchema,
            keywords=["long an", "bhxh long an"],
            priority=2,   # ưu tiên cao nhất
        )
    """
    if name in SCHEMA_REGISTRY:
        # Ghi đè schema cũ (cho phép hot-reload trong admin panel)
        pass
    SCHEMA_REGISTRY[name] = schema_class
    entry = (name, [kw.lower() for kw in keywords])
    if priority >= 2:
        SCHEMA_KEYWORDS.insert(0, entry)
    elif priority == 1:
        # Chèn trước "QUYET_DINH_HANH_CHINH" (generic nhất)
        idx = next(
            (i for i, (n, _) in enumerate(SCHEMA_KEYWORDS)
             if n == "QUYET_DINH_HANH_CHINH"),
            len(SCHEMA_KEYWORDS) - 2,
        )
        SCHEMA_KEYWORDS.insert(idx, entry)
    else:
        SCHEMA_KEYWORDS.append(entry)