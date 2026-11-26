from dataclasses import dataclass, field
from typing import Any, Optional


# Where the inspection happens
INSPECTION_STAGES = {
    "input",
    "tool_call",
    "tool_result",
    "memory_write",
    "memory_read",
    "output"
}


# Unified inspection request
@dataclass
class DetectionRequest:
    trace_id: str
    stage: str
    content: str

    context: dict[str, Any] = field(default_factory=dict)

    detectors: list[str] = field(default_factory=list)


# Unified detector result
@dataclass
class DetectionResult:
    detector: str

    detected: bool

    score: Optional[float] = None

    category: Optional[str] = None

    severity: str = "low"

    entities: list[dict] = field(default_factory=list)

    evidence: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    error: Optional[str] = None


# Unified policy decision
@dataclass
class PolicyDecision:
    action: str

    reason: str

    matched_detectors: list[str] = field(default_factory=list)


# Full inspection report
@dataclass
class InspectionReport:
    trace_id: str

    stage: str

    results: list[DetectionResult]

    decision: PolicyDecision

    audit_pending: list[str] = field(default_factory=list)