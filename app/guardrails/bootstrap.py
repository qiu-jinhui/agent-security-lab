from app.guardrails.registry import DetectorRegistry
from app.guardrails.engine import DetectionEngine

from app.guardrails.detectors.pii import (
    PresidioPIIDetector
)

from app.guardrails.detectors.gliner2_runtime import (
    get_gliner2_runtime
)

from app.guardrails.detectors.gliner2_pii import (
    GLiNER2PIIDetector
)

from app.guardrails.detectors.gliner2_jailbreak import (
    GLiNER2JailbreakDetector
)

from app.guardrails.detectors.gliner2_harmful import (
    GLiNER2HarmfulDetector
)

from app.guardrails.detectors.gliner2_response import (
    GLiNER2ResponseSafetyDetector
)

from app.policies.engine import PolicyEngine

def build_guardrail_engine(
        include_presidio=True,
        include_gliner2=True,
        device="cpu"
):

    registry = DetectorRegistry()

    if include_presidio: 

        registry.register(
            PresidioPIIDetector(),
            mode="blocking"
        )

    if include_gliner2:

        runtime = get_gliner2_runtime(device)

        registry.register(
            GLiNER2PIIDetector(runtime),
            mode="blocking"
        )

        registry.register(
            GLiNER2JailbreakDetector(runtime),
            mode="blocking"
        )

        registry.register(
            GLiNER2HarmfulDetector(runtime),
            mode="blocking"
        )

        registry.register(
            GLiNER2ResponseSafetyDetector(runtime),
            mode="blocking"
        )

    policy_engine = PolicyEngine()

    engine = DetectionEngine(
        registry=registry,
        policy_engine=policy_engine
    )

    return engine

