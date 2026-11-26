from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from app.guardrails.detectors.base import BaseDetector
from app.guardrails.schemas import (
    DetectionRequest,
    DetectionResult
)
from app.guardrails.entity_schema import normalize_entity

class PresidioPIIDetector(BaseDetector):

    name = "pii"
    version = "0.1.0"

    DEFAULT_ENTITIES = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "US_SSN",
        "IBAN_CODE",
        "IP_ADDRESS",
        "LOCATION"
    ]

    HIGH_RISK_ENTITIES = [
        "CREDIT_CARD",
        "US_SSN",
        "IBAN_CODE"
    ]

    def __init__(
        self,
        entities=None,
        score_threshold=0.35,
        language="en"
    ):

        self.entities = entities or self.DEFAULT_ENTITIES
        self.score_threshold = score_threshold
        self.language = language

        configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {
                    "lang_code": "en",
                    "model_name": "en_core_web_sm"
                }
            ]
        }

        provider = NlpEngineProvider(
            nlp_configuration=configuration
        )

        nlp_engine = provider.create_engine()

        self.analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["en"]
        )

    def detect(
        self,
        request: DetectionRequest
    ) -> DetectionResult:

        if request.stage not in {
            "input",
            "tool_result",
            "memory_write",
            "memory_read",
            "output"
        }:
            return DetectionResult(
                detector=self.name,
                detected=False,
                category=None,
                metadata={
                    "reason": "stage_not_supported"
                }
            )

        if not request.content:
            return DetectionResult(
                detector=self.name,
                detected=False
            )

        findings = self.analyzer.analyze(
            text=request.content,
            language=self.language,
            entities=self.entities,
            score_threshold=self.score_threshold
        )

        detected_entities = []

        for finding in findings:

            detected_entities.append(normalize_entity(
                source_entity_type=finding.entity_type,
                start=finding.start,
                end=finding.end,
                score=finding.score
            ))

        detected = len(detected_entities) > 0

        high_risk = any(
            item["source_entity_type"] in self.HIGH_RISK_ENTITIES
            for item in detected_entities
        )

        severity = (
            "high" if high_risk
            else "medium" if detected
            else "low"
        )

        return DetectionResult(
            detector=self.name,
            detected=detected,
            score=max(
                (
                    item["score"]
                    for item in detected_entities
                ),
                default=0.0
            ),
            category="pii_detected" if detected else None,
            severity=severity,
            entities=detected_entities,
            metadata={
                "framework": "presidio",
                "language": self.language,
                "entity_count": len(detected_entities),
                "threshold": self.score_threshold
            }
        )