from app.guardrails.schemas import (
    DetectionRequest,
    INSPECTION_STAGES,
)


STAGE_DETECTORS = {
    "input": [
        "pii",
        "gliner2_pii",
        "gliner2_jailbreak",
        "gliner2_harmful",
    ],
    "tool_result": [
        "pii",
        "gliner2_pii",
        "gliner2_jailbreak",
        "gliner2_harmful",
    ],
    "output": [
        "pii",
        "gliner2_pii",
        "gliner2_harmful",
        "gliner2_response",
    ],
}


class AgentSecurityRuntime:

    def __init__(self, detection_engine):
        self.detection_engine = detection_engine

    def inspect(
        self,
        stage: str,
        content: str,
        trace_id: str,
        context: dict | None = None,
    ):

        if stage not in INSPECTION_STAGES:
            raise ValueError(
                f"Unsupported inspection stage: {stage}"
            )

        if not isinstance(content, str):
            raise TypeError("Content must be a string")

        if not trace_id:
            raise ValueError("trace_id is required")

        detectors = STAGE_DETECTORS.get(stage)

        # Tool calls are protected by the deterministic
        # ToolExecutionGateway, not semantic detectors.
        if detectors is None:
            return None

        available = {
            item["name"]
            for item in self.detection_engine.registry.list_detectors()
        }

        selected = [
            name for name in detectors
            if name in available
        ]

        if not selected:
            raise RuntimeError(
                f"No detectors configured for stage: {stage}"
            )

        request = DetectionRequest(
            trace_id=trace_id,
            stage=stage,
            content=content,
            context=context or {},
            detectors=selected,
        )

        return self.detection_engine.inspect(request)

    @staticmethod
    def is_allowed(report) -> bool:
        return (
            report is not None
            and report.decision.action == "ALLOW"
        )
