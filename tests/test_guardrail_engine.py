from app.guardrails.schemas import DetectionRequest
from app.guardrails.registry import DetectorRegistry
from app.guardrails.engine import DetectionEngine
from app.guardrails.detectors.demo import DemoDetector
from app.policies.engine import PolicyEngine

def build_engine():

    registry = DetectorRegistry()

    registry.register(
        DemoDetector(),
        mode="blocking"
    )

    return DetectionEngine(
        registry=registry,
        policy_engine=PolicyEngine()
    )

def test_normal_content(): 

    engine = build_engine()

    request = DetectionRequest(
        trace_id="trace-001",
        stage="input",
        content="Hello, how are you?",
        detectors=["demo_detector"]
    )

    report = engine.inspect(request)

    assert report.decision.action == "ALLOW"

def test_malicious_content():

    engine = build_engine()

    request = DetectionRequest(
        trace_id="trace-002",
        stage="input",
        content="This is malicious content",
        detectors=["demo_detector"]
    )

    report = engine.inspect(request)

    assert report.decision.action == "BLOCK"

    assert "demo_detector" in (
        report.decision.matched_detectors
    )