import re
import unicodedata
import difflib

class DocumentExtractor:

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = text.replace("đ", "d").replace("Đ", "d")
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def extract(self, raw_text: str, words: list = None) -> dict:
        co_quan = ""
        if words:
            co_quan = self._extract_co_quan_by_position(words)
            # Kết quả quá ngắn (< 3 từ) thì tìm tiếp ở giữa trang
            if not co_quan or len(co_quan.split()) < 3:
                co_quan = self._extract_co_quan_by_center(words)
        if not co_quan:
            co_quan = self._extract_co_quan(raw_text)

        return {
            "ten_loai_van_ban": self._extract_ten_loai(raw_text)   or None,
            "so_van_ban":       self._extract_so_van_ban(raw_text) or None,
            "ngay_thang_nam":   self._extract_ngay(raw_text)       or None,
            "co_quan_ban_hanh": co_quan                            or None,
        }

    def _extract_ten_loai(self, text: str) -> str:
        header     = text[:300]
        normalized = self._normalize(header)
        keywords   = {
            # Văn bản tòa án
            "quyet dinh":        "Quyết định",
            "quyen dinh":        "Quyết định",   # OCR đọc sai
            "ban an so":         "Bản án",
            "ban an":            "Bản án",
            "bien ban hop":      "Biên bản họp",
            "bien ban kiem tra": "Biên bản kiểm tra",
            "bien ban":          "Biên bản",
            # Văn bản hành chính
            "cong van":          "Công văn",
            "nghi quyet":        "Nghị quyết",
            "nghi dinh":         "Nghị định",
            "thong tu":          "Thông tư",
            "thong bao":         "Thông báo",
            "chi thi":           "Chỉ thị",
            "ke hoach":          "Kế hoạch",
            "bao cao":           "Báo cáo",
            "to trinh":          "Tờ trình",
            "hop dong":          "Hợp đồng",
            "giay chung nhan":   "Giấy chứng nhận",
            "giay phep":         "Giấy phép",
            "giay uy quyen":     "Giấy ủy quyền",
            "giay xac nhan":     "Giấy xác nhận",
            "van ban":           "Văn bản",
            "phuong an":         "Phương án",
            "de an":             "Đề án",
            "huong dan":         "Hướng dẫn",
            # Đơn từ
            "don khoi kien":     "Đơn khởi kiện",
            "don khang cao":     "Đơn kháng cáo",
            "don to cao":        "Đơn tố cáo",
            "don to":            "Đơn tố cáo",
            "don kieu nai":      "Đơn khiếu nại",
            "don de nghi":       "Đơn đề nghị",
            "don xin":           "Đơn xin",
            "don":               "Đơn",
        }
        for key, value in keywords.items():
            if key in normalized:
                return value

        # Fuzzy fallback
        candidates = list(keywords.keys())
        close = difflib.get_close_matches(normalized[:50], candidates, n=1, cutoff=0.6)
        if close:
            return keywords[close[0]]
        return ""

    def _extract_so_van_ban(self, text: str) -> str:
        header   = text[:400]
        patterns = [
            r"[Ss][ôo][t]?\s*:\s*([0-9]+\s*/[^\s,;:]+)",
            r"[Ss]ố[t]?\s*:\s*([0-9]+\s*/[^\s,;:]+)",
            r"[Ss]ố[t]?\s*:\s*([0-9]+/[^\s,;:]+)",
            r"[Ss]ố[t]?\s+([0-9]+/[^\s,;:]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, header, re.MULTILINE)
            if match:
                result = match.group(1).strip(".,;: ")
                result = result.replace(" ", "")
                return result
        return ""

    def _extract_ngay(self, text: str) -> str:
        patterns = [
            r",\s*[Nn]gày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",
            r"[Nn]gày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",
            r"[ÀàẤấÂâẦầẢảÃãẬậ]y\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",
            r"[Nn]gày\s*:\s*(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{4})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                d, m, y = match.groups()
                return f"{d}/{m}/{y}"
        return ""

    def _extract_co_quan_by_position(self, words) -> str:
        if not words:
            return ""
        stop_words = {
            "CỘNG", "CỌNG", "HOÀ", "HÒA", "HOA", "CỘỌNG",
            "XÃ", "XA", "HỘI", "HOI", "CHỦ", "CHU",
            "NGHĨA", "NGHIA", "VIỆT", "VIET", "NAM", "NAV",
            "Độc", "độc", "DANH", "NƯỚC", "NUOC",
            "QUYÉẾT", "QUYÉET", "VA", "VÀ", "TẠI",
            "ĐƠN", "TÓ", "CÁO",
            "QUYẾT", "QUYÉT", "QUYÊT", "ĐỊNH", "ĐÌNH",
            "BẢN", "BIÊN", "CÔNG", "VĂN",
            "NGHỊ", "THÔNG", "TƯ", "CHỈ", "THỊ",
        }
        max_x    = max(w.x for w in words)
        mid_x    = max_x / 2
        max_y    = max(w.y for w in words)
        top_zone = max_y * 0.15

        left_words = [
            w for w in words
            if w.x < mid_x
            and w.y < top_zone
            and w.text.strip(".,;:-'\"").isupper()
            and len(w.text.strip(".,;:-'\"")) > 1
            and not any(c.isdigit() for c in w.text)
            and "/" not in w.text
            and ")" not in w.text
            and "(" not in w.text
            and w.text.strip(".,;:-'\"") not in stop_words
        ]

        if not left_words:
            return ""

        left_words.sort(key=lambda w: (w.y, w.x))
        lines   = []
        current = [left_words[0]]

        for word in left_words[1:]:
            if abs(word.y - current[0].y) < 20:
                current.append(word)
            else:
                lines.append(current)
                current = [word]
        lines.append(current)

        result = " ".join(
            " ".join(w.text for w in sorted(line, key=lambda w: w.x))
            for line in lines
        )
        return result.strip(".,;:-'\"")
    
    def _extract_co_quan_by_center(self, words) -> str:
        if not words:
            return ""

        co_quan_keywords = {"TÒA", "ỦY", "UỶ", "BỘ", "CỤC", "SỞ", "VIỆN"}

        stop_words = {
            "CỘNG", "CỌNG", "HOÀ", "HÒA", "HOA",
            "XÃ", "XA", "HỘI", "CHỦ", "CHU",
            "NGHĨA", "VIỆT", "NAM", "NAV",
            "Độc", "độc", "DANH", "NƯỚC",
            "QUYẾT", "QUYÉT", "ĐỊNH", "ĐÌNH",
            "BẢN", "BIÊN", "CÔNG", "VĂN",
            "NGHỊ", "THÔNG", "TƯ", "CHỈ", "THỊ",
            "ĐƠN", "TÓ", "CÁO",
        }

        max_y    = max(w.y for w in words)
        top_zone = max_y * 0.5  # tìm trong 50% đầu trang

        # Lọc từ IN HOA, không chứa số, không có ký tự đặc biệt
        center_words = [
            w for w in words
            if w.y < top_zone
            and w.text.strip(".,;:-'\"").isupper()
            and len(w.text.strip(".,;:-'\"")) > 1
            and not any(c.isdigit() for c in w.text)
            and "/" not in w.text
            and ")" not in w.text
            and "(" not in w.text
            and w.text.strip(".,;:-'\"") not in stop_words
        ]

        if not center_words:
            return ""

        # Gom thành dòng
        center_words.sort(key=lambda w: (w.y, w.x))
        lines   = []
        current = [center_words[0]]

        for word in center_words[1:]:
            if abs(word.y - current[0].y) < 20:
                current.append(word)
            else:
                lines.append(current)
                current = [word]
        lines.append(current)

        # Tìm dòng đầu tiên có từ khóa cơ quan
        result_lines = []
        for line in lines:
            line_text = " ".join(w.text for w in sorted(line, key=lambda w: w.x))
            if any(kw in line_text for kw in co_quan_keywords):
                result_lines.append(line_text)
                # Lấy thêm dòng tiếp theo nếu cũng IN HOA (tối đa 1 dòng)
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    next_text = " ".join(w.text for w in sorted(lines[idx+1], key=lambda w: w.x))
                    if any(kw in next_text for kw in co_quan_keywords):
                        result_lines.append(next_text)
                break

        if not result_lines:
            return ""

        return " ".join(result_lines).strip(".,;:-'\"")
    
    def _extract_co_quan(self, text: str) -> str:
        """Fallback dùng regex khi không có words"""
        patterns = [
            # Tòa án các cấp
            r"(TÒA ÁN NHÂN \S+(?:\s+\S+){1,5})(?=\s+(?:CỘNG|Độc|độc|Với|TẠI|tại|\-))",
            r"(TÒA ÁN NHÂN DÂN KHU VỰC\s+\S+(?:\s+\S+){1,3})",
            r"(TÒA ÁN NHÂN DÂN CẤP CAO(?:\s+\S+){1,3})",
            # Ủy ban nhân dân
            r"((?:ỦY BAN|UỶ BAN) NHÂN DÂN(?:\s+\S+){1,4})(?=\s+(?:Độc|độc|\-))",
            r"(UBND \S+(?: \S+)?)",
            # Viện kiểm sát
            r"(VIỆN KIỂM SÁT NHÂN DÂN(?:\s+\S+){1,4})",
            r"(VIỆN KIỂM SÁT(?:\s+\S+){1,3})",
            # Tòa án chữ thường
            r"(Tòa án nhân dân(?:\s+\S+){1,4})(?=\s+(?:[-–]|Độc|độc))",
            # Bộ, Cục, Sở, Chi cục, Văn phòng
            r"(BỘ \S+(?: \S+){1,3})",
            r"(CỤC \S+(?: \S+){1,2})",
            r"(SỞ \S+(?: \S+){1,2})",
            r"(CHI CỤC \S+(?: \S+){1,2})",
            r"(VĂN PHÒNG \S+(?: \S+){1,2})",
            # Hội đồng nhân dân
            r"(HỘI ĐỒNG NHÂN DÂN(?:\s+\S+){1,4})",
            # Ban
            r"(BAN \S+(?: \S+){1,2})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip(".,;:")
        return ""