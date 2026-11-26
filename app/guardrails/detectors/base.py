from abc import ABC, abstractmethod

from app.guardrails.schemas import (
    DetectionRequest, 
    DetectionResult
)

class BaseDetector(ABC):

    name: str = "base"
    version: str = "0.1.0"

    @abstractmethod
    def detect(
        self,
        request: DetectionRequest
    ) -> DetectionResult:
        pass