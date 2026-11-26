from app.guardrails.schemas import DetectionRequest
from app.guardrails.bootstrap import build_guardrail_engine

def test_email_detection():

    engine = build_guardrail_engine()

    request = DetectionRequest(
        trace_id="pii-test-001",
        stage="input",
        content="Contact John at john.smith@example.com. ",
        detectors=['pii']
    )

    report = engine.inspect(request)

    pii_result = next(
        result
        for result in report.results
        if result.detector == 'pii'
    )

    assert pii_result.detected is True

    entity_types = {
        entity["entity_type"]
        for entity in pii_result.entities
    }

    assert "EMAIL_ADDRESS" in entity_types

    assert report.decision.action == "REQUIRE_APPROVAL"

def test_normal_content():

    engine = build_guardrail_engine()

    request = DetectionRequest(
        trace_id="pii-test-001",
        stage="input",
        content="The Kubernetes cluster is running normally. ",
        detectors=['pii']
    )

    report = engine.inspect(request)

    pii_result = report.results[0]

    assert pii_result.detected is False

    assert report.decision.action == "ALLOW"

def test_credit_card_detection():

    engine = build_guardrail_engine()

    request = DetectionRequest(
        trace_id="pii-test-003",
        stage="output",
        content="Test card: 4111111111111111",
        detectors=["pii"]
    )

    report = engine.inspect(request)

    pii_result = report.results[0]

    assert pii_result.detected is True

    assert any(
        entity["entity_type"] == "PAYMENT_CARD"
        for entity in pii_result.entities
    )

    assert any(
        entity["source_entity_type"] == "CREDIT_CARD"
        for entity in pii_result.entities
    )

    assert report.decision.action == "BLOCK"