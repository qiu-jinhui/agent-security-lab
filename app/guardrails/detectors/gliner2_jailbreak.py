from app.guardrails.detectors.base import BaseDetector
from app.guardrails.detectors.gliner2_runtime import (
    get_gliner2_runtime
)
from app.guardrails.schemas import (
    DetectionRequest,
    DetectionResult
)

class GLiNER2JailbreakDetector(BaseDetector):

    name = "gliner2_jailbreak"
    version = "0.1.0"

    LABELS = [
        "prompt_injection",
        "jailbreak_attempt",
        "policy_evasion",
        "instruction_override",
        "system_prompt_exfiltration",
        "data_exfiltration",
        "roleplay_bypass",
        "hypothetical_bypass",
        "obfuscated_attack",
        "multi_step_attack",
        "social_engineering"
    ]

    SUPPORTED_STAGES = {
        "input",
        "tool_result",
        "memory_write",
        "memory_read"
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

        task = {
            "labels": self.LABELS,
            "multi_label": True,
            "cls_threshold": 0.4
        }

        response = self.runtime.classify(
            request.content,
            {
                "jailbreak_detection": task
            },
            threshold=self.threshold
        )

        labels = response.get(
            "jailbreak_detection", []
        )

        unsafe = response.get(
            "prompt_safety"
        ) == "unsafe"

        detected = bool(labels) or unsafe

        return DetectionResult(
            detector=self.name,
            detected=detected,
            score=None,
            category=(
                ",".join(labels)
                if labels else
                "unsafe_prompt"
                if unsafe else None
            ),
            severity="high" if detected else "low",
            evidence=labels,
            metadata={
                "model": "GLiNER2",
                "prompt_safety": response.get(
                    "prompt_safety"
                ),
                "labels": labels,
                "threshold": self.threshold
            }
        )