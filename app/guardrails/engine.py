from app.guardrails.schemas import (
    DetectionRequest,
    InspectionReport,
    DetectionResult,
    PolicyDecision
)

class DetectionEngine:

    def __init__(self, registry, policy_engine):
        self.registry = registry
        self.policy_engine = policy_engine

    def inspect(self, request: DetectionRequest):

        results = []

        requested = request.detectors or [
            item["name"]
            for item in self.registry.list_detectors()
        ]

        for name in requested:

            detector = self.registry.get(name)

            if detector is None:
                raise ValueError(
                    f"Unknown detector: {name}"
                )

            if self.registry.get_mode(name) != "blocking":
                continue

            try: 
                result = detector.detect(request)

                results.append(result)

            except Exception as exc:

                results.append(
                    DetectionResult(
                        detector=name,
                        detected=True,
                        category="detector_error",
                        severity="critical",
                        error=str(exc)
                    )
                )

        decision = self.policy_engine.evaluate(results)

        audit_pending = [
            name
            for name in requested
            if self.registry.get(name) is not None
            and self.registry.get_mode(name) == "audit"
        ]

        return InspectionReport(
            trace_id=request.trace_id,
            stage=request.stage,
            results=results,
            decision=decision,
            audit_pending=audit_pending
        )
