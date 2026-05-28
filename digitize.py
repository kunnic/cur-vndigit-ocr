from __future__     import annotations

from dataclasses    import dataclass
from typing         import Any, Dict, List, Optional, Union

import numpy as np

from src.preprocessing.preprocess   import PreprocessResult, Preprocessing
from src.ocr.ocr                    import BaseOCR, OCRResult
from src.utils.extracting.base      import BaseExtractor, ExtractorResult
from src.utils.extracting.gemini    import GeminiExtractor, GeminiParams
from src.utils.extracting.gemma     import GemmaExtractor, Gemma4Params
from src.utils.extracting.correction.autocorrect import AutoCorrector

@dataclass
class DigitizeResult:

    # Images
    original_image: np.ndarray
    preprocessed_image: np.ndarray

    # Preprocessing
    preprocess: PreprocessResult

    # OCR
    ocr: OCRResult

    # Post‑OCR correction
    corrected_texts: Optional[List[str]] = None

    # LLM extraction
    extraction: Optional[ExtractorResult[Any]] = None

@dataclass
class DigitizeConfig:

    preprocessing:  Dict[str, Any] | None = None
    autocorrect:    Dict[str, Any] | None = None
    extraction:     Dict[str, Any] | None = None


def _build_ocr_engine(ocr: BaseOCR) -> BaseOCR:
    return ocr


def _build_autocorrect(config: Dict[str, Any] | None) -> AutoCorrector:
    return AutoCorrector(config or {})


def _build_extractor(config: Dict[str, Any] | None) -> Optional[BaseExtractor]:
    cfg = config or {}
    if not cfg.get("enabled", False):
        return None

    provider = (cfg.get("provider") or "gemini").lower()

    if provider == "gemini":
        gemini_cfg: Dict[str, Any] = cfg.get("gemini", {})
        api_key = gemini_cfg.get("api_key")
        if not api_key:
            raise ValueError("Gemini extraction enabled but 'api_key' is missing")

        params_dict: Dict[str, Any] = gemini_cfg.get("params", {})
        params = GeminiParams(**params_dict) if params_dict else GeminiParams()
        return GeminiExtractor(api_key=api_key, params=params)

    if provider == "gemma":
        gemma_cfg: Dict[str, Any] = cfg.get("gemma", {})
        params_dict: Dict[str, Any] = gemma_cfg.get("params", {})
        params = Gemma4Params(**params_dict) if params_dict else Gemma4Params()
        return GemmaExtractor(params=params)

    raise ValueError(f"Unsupported extraction provider: {provider!r}")

class Digitize:
    def __init__(
        self,
        ocr: BaseOCR,
        config: Dict[str, Any] | None = None,
    ) -> None:
        cfg = DigitizeConfig(**(config or {}))

        self.preprocess = Preprocessing(cfg.preprocessing or {})
        self.ocr_engine = _build_ocr_engine(ocr)
        self.autocorrect = _build_autocorrect(cfg.autocorrect)
        self.extractor = _build_extractor(cfg.extraction)

    def _run_preprocess(self, image: np.ndarray) -> PreprocessResult:
        return self.preprocess.process(image)

    def _run_ocr(self, image: np.ndarray) -> OCRResult:
        return self.ocr_engine.recognize(image)

    def _run_correction(self, ocr_result: OCRResult) -> List[str]:
        correction_result = self.autocorrect.correct_ocr_result(ocr_result)
        return correction_result.corrected_texts

    def _run_extraction(
        self,
        text: str,
    ) -> Optional[ExtractorResult[Any]]:
        if self.extractor is None:
            return None

        return self.extractor.extract(text)

    def _digitize_single(self, image: np.ndarray) -> DigitizeResult:
        pre = self._run_preprocess(image)
        ocr_result = self._run_ocr(pre.image)

        corrected_texts: List[str] | None = None
        if self.autocorrect.enabled:
            corrected_texts = self._run_correction(ocr_result)

        extraction_result: Optional[ExtractorResult[Any]] = None
        if corrected_texts:
            joined_text = "\n".join(corrected_texts)
            extraction_result = self._run_extraction(joined_text)
        else:
            if isinstance(ocr_result.texts, str):
                text_blob = ocr_result.texts
            else:
                text_blob = "\n".join(block.text for block in ocr_result.texts)
            extraction_result = self._run_extraction(text_blob)

        return DigitizeResult(
            original_image      = image,
            preprocessed_image  = pre.image,
            preprocess          = pre,
            ocr                 = ocr_result,
            corrected_texts     = corrected_texts,
            extraction          = extraction_result,
        )
    
    def _digitize_batch(self, images: List[np.ndarray]) -> List[DigitizeResult]:
        pres: List[PreprocessResult] = [self._run_preprocess(img) for img in images]

        ocr_inputs = [p.image for p in pres]
        ocr_outputs = self.ocr_engine.recognize(ocr_inputs)
        if not isinstance(ocr_outputs, list):
            ocr_outputs = [ocr_outputs]

        results: List[DigitizeResult] = []
        for original, pre, ocr_result in zip(images, pres, ocr_outputs):
            corrected_texts: List[str] | None = None
            if self.autocorrect.enabled:
                corrected_texts = self._run_correction(ocr_result)

            if corrected_texts:
                text_blob = "\n".join(corrected_texts)
            else:
                if isinstance(ocr_result.texts, str):
                    text_blob = ocr_result.texts
                else:
                    text_blob = "\n".join(block.text for block in ocr_result.texts)

            extraction_result = self._run_extraction(text_blob)

            results.append(
                DigitizeResult(
                    original_image      = original,
                    preprocessed_image  = pre.image,
                    preprocess          = pre,
                    ocr                 = ocr_result,
                    corrected_texts     = corrected_texts,
                    extraction          = extraction_result,
                )
            )

        return results

    def digitize(
        self,
        image: Union[np.ndarray, List[np.ndarray]],
    ) -> Union[DigitizeResult, List[DigitizeResult]]:
        if isinstance(image, list):
            return self._digitize_batch(image)
        return self._digitize_single(image)