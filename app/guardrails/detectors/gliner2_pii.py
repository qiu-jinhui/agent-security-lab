from app.guardrails.detectors.base import BaseDetector
from app.guardrails.detectors.gliner2_runtime import (
    get_gliner2_runtime
)
from app.guardrails.schemas import (
    DetectionRequest,
    DetectionResult
)
from app.guardrails.entity_schema import normalize_entity

class GLiNER2PIIDetector(BaseDetector): 

    name = "gliner2_pii"
    version = "0.1.0"

    LABELS = [
        "person",
        "full_name",
        "first_name",
        "last_name",
        "organization",
        "email",
        "phone_number",
        "address",
        "date_of_birth",
        "passport_number",
        "national_id_number",
        "tax_id",
        "bank_account",
        "iban",
        "credit_card",
        "card_cvv",
        "ip_address",
        "username",
        "password",
        "api_key",
        "access_token",
        "recovery_code"
    ]

    HIGH_RISK = {
        "PASSPORT_NUMBER",
        "NATIONAL_ID_NUMBER",
        "TAX_ID",
        "BANK_ACCOUNT",
        "IBAN",
        "CREDIT_CARD",
        "CARD_CVV",
        "PASSWORD",
        "API_KEY",
        "ACCESS_TOKEN",
        "RECOVERY_CODE"
    }

    SUPPORTED_STAGES = {
        "input",
        "tool_result",
        "memory_write",
        "memory_read",
        "output"
    }

    def __init__(self, runtime=None, threshold=0.5):
        self.runtime = runtime or get_gliner2_runtime()
        self.threshold = threshold

    def detect(self, request: DetectionRequest):

        if request.stage not in self.SUPPORTED_STAGES:
            return DetectionResult(
                detector=self.name,
                detected=False,
                metadata={
                    "reason": "stage_not_supported"
                }
            )

        if not request.content:
            return DetectionResult(
                detector=self.name,
                detected=False
            )

        response = self.runtime.extract_entities(
            request.content,
            self.LABELS,
            threshold=self.threshold
        )

        entities = response.get("entities", {})

        findings = []

        for label, items in entities.items():

            for item in items:

                findings.append(
                    normalize_entity(
                        source_entity_type=label,
                        start=item.get("start"),
                        end=item.get("end"),
                        score=item.get("confidence", 0)
                    )
                )

        detected = bool(findings)

        high_risk = any(
            item["source_entity_type"] in self.HIGH_RISK
            for item in findings
        )

        return DetectionResult(
            detector=self.name,
            detected=detected,
            score=max(
                (item["score"] for item in findings),
                default=0.0
            ),
            category="pii_detected" if detected else None,
            severity=(
                "high" if high_risk
                else "medium" if detected
                else "low"
            ),
            entities=findings,
            metadata={
                "model": "GLiNER2",
                "model_name": self.runtime.MODEL_NAME,
                "threshold": self.threshold,
                "entity_count": len(findings)
            }
        )