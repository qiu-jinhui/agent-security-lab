import pytest

from app.security.agent_security_runtime import (
    AgentSecurityRuntime,
)

from app.guardrails.schemas import (
    InspectionReport,
    PolicyDecision,
)


class MockRegistry:

    def list_detectors(self):
        return [
            {"name": "pii"},
            {"name": "gliner2_pii"},
            {"name": "gliner2_jailbreak"},
            {"name": "gliner2_harmful"},
            {"name": "gliner2_response"},
        ]


class MockDetectionEngine:

    def __init__(self, action="ALLOW"):
        self.registry = MockRegistry()
        self.action = action
        self.last_request = None

    def inspect(self, request):
        self.last_request = request

        return InspectionReport(
            trace_id=request.trace_id,
            stage=request.stage,
            results=[],
            decision=PolicyDecision(
                action=self.action,
                reason="Mock decision",
            ),
        )


@pytest.fixture
def engine():
    return MockDetectionEngine()


@pytest.fixture
def runtime(engine):
    return AgentSecurityRuntime(engine)


def test_input_uses_expected_detectors(runtime, engine):

    report = runtime.inspect(
        stage="input",
        content="Hello",
        trace_id="trace-001",
    )

    assert report.decision.action == "ALLOW"

    assert set(engine.last_request.detectors) == {
        "pii",
        "gliner2_pii",
        "gliner2_jailbreak",
        "gliner2_harmful",
    }


def test_tool_result_uses_jailbreak_detector(
    runtime,
    engine,
):

    runtime.inspect(
        stage="tool_result",
        content="Tool output",
        trace_id="trace-002",
    )

    assert "gliner2_jailbreak" in (
        engine.last_request.detectors
    )


def test_output_uses_response_safety_detector(
    runtime,
    engine,
):

    runtime.inspect(
        stage="output",
        content="Assistant response",
        trace_id="trace-003",
    )

    assert "gliner2_response" in (
        engine.last_request.detectors
    )


@pytest.mark.parametrize(
    "action",
    ["BLOCK", "REQUIRE_APPROVAL"],
)
def test_non_allow_decision_is_not_allowed(action):

    mock_engine = MockDetectionEngine(action=action)
    runtime = AgentSecurityRuntime(mock_engine)

    report = runtime.inspect(
        stage="input",
        content="Test",
        trace_id="trace-004",
    )

    assert runtime.is_allowed(report) is False


def test_allow_decision_is_allowed(runtime):

    report = runtime.inspect(
        stage="input",
        content="Hello",
        trace_id="trace-005",
    )

    assert runtime.is_allowed(report) is True


def test_tool_call_has_no_semantic_inspection(runtime):

    report = runtime.inspect(
        stage="tool_call",
        content='{"tool": "get_weather"}',
        trace_id="trace-006",
    )

    assert report is None
    assert runtime.is_allowed(report) is False


def test_unknown_stage_is_rejected(runtime):

    with pytest.raises(ValueError):
        runtime.inspect(
            stage="unknown",
            content="test",
            trace_id="trace-007",
        )


def test_empty_trace_id_is_rejected(runtime):

    with pytest.raises(ValueError):
        runtime.inspect(
            stage="input",
            content="test",
            trace_id="",
        )
