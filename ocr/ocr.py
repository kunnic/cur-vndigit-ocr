import numpy as np
from dataclasses import dataclass

from abc import ABC, abstractmethod
from typing import List, Union, overload

@dataclass
class OCRResult:
    text: str
    confidence: float
    
class OCRModel(ABC):
    @overload
    def recognize(self, image: np.ndarray) -> OCRResult: ...

    @overload
    def recognize(self, image: List[np.ndarray]) -> List[OCRResult]: ...

    @abstractmethod
    def recognize(
            self, 
            image: Union[np.ndarray, List[np.ndarray]]
        ) -> Union[OCRResult, List[OCRResult]]:
        pass