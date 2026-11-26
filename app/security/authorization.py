from dataclasses import dataclass
from typing import FrozenSet

@dataclass(frozen=True)
class AuthorizationDecision:
    action: str
    reason: str
    role: str
    tool_name: str

    @property
    def allowed(self) -> bool:
        return self.action == "ALLOW"

class ToolAuthorizationEngine:

    def __init__(
        self,
        allowed_tools_by_role: dict[str, set[str]],
        approval_required_tools: set[str] | None = None,
    ):

        self.allowed_tools_by_role = {
            role: frozenset(tools)
            for role, tools in allowed_tools_by_role.items()
        }

        self.approval_required_tools: FrozenSet[str] = (
            frozenset(approval_required_tools or set())
        )

    def authorize(
        self,
        role: str | None,
        tool_name: str,
        registered_tools: set[str]
    ) -> AuthorizationDecision:

        def decision(action: str, reason: str):
            return AuthorizationDecision(
                action=action,
                reason=reason,
                role=role or "anonymous",
                tool_name=tool_name
            )

        if not role:
            return decision(
                "DENY",
                "Missing user role"
            )

        if tool_name not in registered_tools:
            return decision(
                "DENY",
                "Unknown or unregistered tool"
            )

        if role not in self.allowed_tools_by_role:
            return decision(
                "DENY",
                "Unknown or unauthorized role"
            )

        allowed_tools = self.allowed_tools_by_role[role]

        if tool_name not in allowed_tools:
            return decision(
                "DENY",
                "Role is not authorized to use this tool"
            )

        if tool_name in self.approval_required_tools:
            return decision(
                "REQUIRE_APPROVAL",
                "TOol requires human approval"
            )

        return decision(
            "ALLOW",
            "Tool invocation authorized"
        )