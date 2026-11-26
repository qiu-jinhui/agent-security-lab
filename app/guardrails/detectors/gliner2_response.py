from app.guardrails.detectors.base import BaseDetector
from app.guardrails.detectors.gliner2_runtime import (
    get_gliner2_runtime
)
from app.guardrails.schemas import (
    DetectionRequest,
    DetectionResult
)

class GLiNER2ResponseSafetyDetector(BaseDetector):

    name = "gliner2_response"
    version = "0.1.0"

    SUPPORTED_STAGES = {"output"}

    def __init__(self, runtime=None, threshold=0.5):

        self.runtime = runtime or get_gliner2_runtime()
        self.threshold = threshold

    def detect(self, request: DetectionRequest):

        if request.stage not in self.SUPPORTED_STAGES:
            return DetectionResult(
                detector=self.name,
                detected=False
            )

        response = self.runtime.classify(
            request.content,
            {
                "response_safety": ["safe", "unsafe"],
                "response_refusal": [
                    "refusal",
                    "compliance"
                ]
            },
            threshold=self.threshold
        )

        safety = response.get("response_safety")
        refusal = response.get("response_refusal")

        # Refusal is not itself a safety violation.
        detected = safety == "unsafe"

        return DetectionResult(
            detector=self.name,
            detected=detected,
            category=(
                "unsafe_response" if detected else None
            ),
            severity="high" if detected else "low",
            evidence=[safety] if safety else [],
            metadata={
                "model": "GLiNER2",
                "response_safety": safety,
                "response_refusal": refusal,
                "threshold": self.threshold
            }
        )
