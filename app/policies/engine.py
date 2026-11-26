from app.guardrails.schemas import PolicyDecision

class PolicyEngine:

    def evaluate(self, results):

        matched = [
            result
            for result in results
            if result.detected
        ]

        errors = [
            result
            for result in results
            if result.error is not None
        ]

        if errors:
            return PolicyDecision(
                action="BLOCK",
                reason="One or more blocking detectors failed",
                matched_detectors=[
                    result.detector for result in errors
                ]
            )

        critical = [
            result
            for result in matched
            if result.severity in ("critical", "high")
        ]

        if critical:
            return PolicyDecision(
                action="BLOCK",
                reason="High-risk security violation detected",
                matched_detectors=[
                    result.detector for result in critical
                ]
            )

        medium = [
            result
            for result in matched
            if result.severity == "medium"
        ]

        if medium:
            return PolicyDecision(
                action="REQUIRE_APPROVAL",
                reason="Medium-risk finding requires review",
                matched_detectors=[
                    result.detector for result in medium
                ]
            )

        return PolicyDecision(
            action="ALLOW",
            reason="No blocking security findings",
            matched_detectors=[]
        )