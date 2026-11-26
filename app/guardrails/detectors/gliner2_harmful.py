
from app.guardrails.detectors.base import BaseDetector
from app.guardrails.detectors.gliner2_runtime import (
    get_gliner2_runtime
)
from app.guardrails.schemas import (
    DetectionRequest,
    DetectionResult
)

class GLiNER2HarmfulDetector(BaseDetector):

    name = "gliner2_harmful"
    version = "0.1.0"

    LABELS = [
        "violence_and_weapons",
        "non_violent_crime",
        "sexual_content",
        "hate_and_discrimination",
        "self_harm_and_suicide",
        "pii_exposure",
        "misinformation",
        "copyright_violation",
        "child_safety",
        "political_manipulation",
        "unethical_conduct",
        "regulated_advice",
        "privacy_violation",
        "other"
    ]

    SUPPORTED_STAGES = {
        "input",
        "tool_result",
        "output"
    }

    def __init__(self, runtime=None, threshold=0.5):

        self.runtime = runtime or get_gliner2_runtime()
        self.threshold = threshold

    def detect(self, request: DetectionRequest):

        if request.stage not in self.SUPPORTED_STAGES:
            return DetectionResult(
                detector=self.name,
                detected=False
            )

        task_name = (
            "prompt_toxicity"
            if request.stage == "input"
            else "response_toxicity"
        )

        task = {
            "labels": self.LABELS,
            "multi_label": True,
            "cls_threshold": 0.4
        }

        response = self.runtime.classify(
            request.content,
            {
                task_name: task
            },
            threshold=self.threshold
        )

        labels = response.get(task_name, [])

        detected = bool(labels)

        return DetectionResult(
            detector=self.name,
            detected=detected,
            category=",".join(labels) if labels else None,
            severity="high" if detected else "low",
            evidence=labels,
            metadata={
                "model": "GLiNER2",
                "task": task_name,
                "labels": labels,
                "prompt_safety": response.get(
                    "prompt_safety"
                ),
                "threshold": self.threshold
            }
        )
