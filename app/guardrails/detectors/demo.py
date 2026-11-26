from app.guardrails.detectors.base import BaseDetector
from app.guardrails.schemas import DetectionResult

class DemoDetector(BaseDetector):

    name = "demo_detector"

    def detect(self, request):

        suspicious = "malicious" in request.content.lower()

        return DetectionResult(
            detector=self.name,
            detected=suspicious,
            score=0.99 if suspicious else 0.01,
            category="suspicious_content" if suspicious else None,
            severity="high" if suspicious else "low"
        )