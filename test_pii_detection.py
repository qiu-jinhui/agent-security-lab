from pprint import pprint

from app.guardrails.bootstrap import build_guardrail_engine
from app.guardrails.schemas import DetectionRequest

engine = build_guardrail_engine()

samples = [
    {
        "id": "sample-001",
        "text": "Contact John at john.smith@example.com."
    },
    {
        "id": "sample-002",
        "text": "Please call me at 415-555-0132."
    },
    {
        "id": "sample-003",
        "text": "The Kubernetes cluster is healthy."
    }
]

for sample in samples:

    request = DetectionRequest(
        trace_id=sample["id"],
        stage="input",
        content=sample["text"],
        detectors=["pii"]
    )

    report = engine.inspect(request)

    print("\n===== SAMPLE =====")
    print(sample["id"])

    print("\n===== DETECTION RESULTS =====")

    for result in report.results:
        pprint({
            "detector": result.detector,
            "detected": result.detected,
            "score": result.score,
            "severity": result.severity,
            "entities": result.entities
        })

    print("\n===== POLICY DECISION =====")
    print(report.decision.action)
    print(report.decision.reason)