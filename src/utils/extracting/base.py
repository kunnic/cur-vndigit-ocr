# -- built in --
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import overload, Generic, TypeVar, TypeAlias, Optional, Type, Any, Dict, List

# -- third party --
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor

T = TypeVar("T", bound=BaseModel)
TextInput: TypeAlias = str | list[str]


# ── DEFINE ────────────────────────────────────────────────────────────────────
@dataclass
class ExtractorResult(Generic[T]):
    record: Optional[T] = None
    schema_used: str = ""
    # extracted_dynamic_data: {field_name → {value, confidence, flagged, missing, ...}}
    extracted_dynamic_data: Optional[Dict[str, Any]] = None
    confidence_overall: float = 0.0
    fill_rate: float = 0.0
    error: Optional[str] = None
    raw_output_sample: str = ""

    # ── API Contract output ───────────────────────────────────────────────────
    def to_dict(self, document_id: str = "") -> dict:
        """
        Xuất ra chuẩn API Contract của hệ thống VN-Digitize.

        Cấu trúc:
        {
          "document_id":        str,
          "classification":     str,   # tên schema (loại văn bản)
          "confidence_overall": float,
          "fill_rate":          float,
          "error":              str | null,
          "metadata": [
            {
              "field_name":  str,
              "value":       str | null,
              "confidence":  float | null,   # null nếu field missing
              "flagged":     bool,
              "missing":     bool
              # "warning":   str  (tùy chọn, có khi cross-validate phát hiện lỗi)
            },
            ...
          ]
        }
        """
        metadata = self._build_metadata_list()
        return {
            "document_id":        document_id,
            "classification":     self.schema_used,
            "confidence_overall": self.confidence_overall,
            "fill_rate":          self.fill_rate,
            "error":              self.error,
            "metadata":           metadata,
        }

    def _build_metadata_list(self) -> List[dict]:
        """
        Chuyển extracted_dynamic_data (dict[field_name → field_info])
        sang list[dict] theo thứ tự field trong schema.

        Hỗ trợ 2 dạng extracted_dynamic_data:
          - Dạng đầy đủ (từ _score_extraction): giá trị là dict có sẵn các key
          - Dạng đơn giản (record.model_dump()): giá trị là scalar/None
        """
        if not self.extracted_dynamic_data:
            # Fallback sang record nếu không có dynamic data
            if self.record:
                return [
                    {
                        "field_name":  k,
                        "value":       v,
                        "confidence":  None,
                        "flagged":     False,
                        "missing":     v is None,
                    }
                    for k, v in self.record.model_dump().items()
                ]
            return []

        metadata: List[dict] = []
        for field_name, field_info in self.extracted_dynamic_data.items():
            if isinstance(field_info, dict):
                # Dạng đầy đủ — copy thẳng, đảm bảo có đủ key bắt buộc
                entry = {
                    "field_name":  field_name,
                    "value":       field_info.get("value"),
                    "confidence":  field_info.get("confidence"),
                    "flagged":     field_info.get("flagged", False),
                    "missing":     field_info.get("missing", field_info.get("value") is None),
                }
                # Chuyển tiếp warning nếu có (từ cross-validation)
                if "warning" in field_info:
                    entry["warning"] = field_info["warning"]
            else:
                # Dạng đơn giản (scalar)
                entry = {
                    "field_name":  field_name,
                    "value":       field_info,
                    "confidence":  None,
                    "flagged":     False,
                    "missing":     field_info is None,
                }
            metadata.append(entry)
        return metadata

    # ── Legacy helpers (giữ lại để tương thích) ──────────────────────────────
    def to_flat_dict(self) -> dict:
        """
        Xuất dạng phẳng (flat) như cũ — tiện debug / logging.
        Không phải API Contract; dùng to_dict() cho backend/frontend.
        """
        return {
            "schema_used":            self.schema_used,
            "confidence_overall":     self.confidence_overall,
            "fill_rate":              self.fill_rate,
            "error":                  self.error,
            "extracted_dynamic_data": self.extracted_dynamic_data,
            "record":                 self.record.model_dump() if self.record else None,
        }

    def __str__(self) -> str:
        parts = [
            f"EXTRACTION RESULT "
            f"(Schema: {self.schema_used} | "
            f"Conf: {self.confidence_overall:.1%} | "
            f"Fill: {self.fill_rate:.1%})"
        ]
        if self.error:
            parts.append(f"  [ERROR]: {self.error}")
        metadata = self._build_metadata_list()
        for m in metadata:
            conf_str  = f"{m['confidence']:.2f}" if m["confidence"] is not None else "N/A"
            flag_str  = " ⚠️"  if m.get("flagged") else ""
            warn_str  = f"  ← {m['warning']}" if m.get("warning") else ""
            parts.append(
                f"  {m['field_name']:<30}: {str(m['value'])!r:<50} "
                f"(conf={conf_str}){flag_str}{warn_str}"
            )
        return "\n".join(parts)


# ── BASE EXTRACTOR ────────────────────────────────────────────────────────────
class BaseExtractor(ABC):
    @overload
    def extract(self, inputs: str,       schema: Optional[Type[T]] = None) -> ExtractorResult[T]: ...
    @overload
    def extract(self, inputs: list[str], schema: Optional[Type[T]] = None) -> list[ExtractorResult[T]]: ...

    def extract(
        self,
        inputs: TextInput,
        schema: Optional[Type[T]] = None,
    ) -> ExtractorResult[T] | list[ExtractorResult[T]]:
        if isinstance(inputs, list):
            return self._extract_batch(inputs, schema)
        return self._extract_single(inputs, schema)

    @abstractmethod
    def _extract_single(
        self, text: str, schema: Optional[Type[T]] = None
    ) -> ExtractorResult[T]:
        pass

    def _extract_batch(
        self, texts: list[str], schema: Optional[Type[T]] = None
    ) -> list[ExtractorResult[T]]:
        # ML/DL models với native batch support nên override method này.
        # Default: ThreadPoolExecutor (direct API song song).
        with ThreadPoolExecutor() as executor:
            return list(
                executor.map(lambda t: self._extract_single(t, schema), texts)
            )