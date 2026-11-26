from app.security.authorization import (
    ToolAuthorizationEngine
)

class ToolExecutionGateway:

    def __init__(
        self,
        authorization_engine: ToolAuthorizationEngine,
        tools: dict
    ):
        self.authorization_engine = authorization_engine
        self.tools = tools

    def execute(
        self,
        role: str | None,
        tool_name: str,
        arguments: dict
    ) -> dict:

        decision = self.authorization_engine.authorize(
            role=role,
            tool_name=tool_name,
            registered_tools=set(self.tools.keys())
        )

        if decision.action == "DENY":
            return {
                "status": "DENIED",
                "reason": decision.reason,
                "tool": tool_name
            }

        if decision.action == "REQUIRE_APPROVAL":
            return {
                "status": "PENDING_APPROVAL",
                "reason": decision.reason,
                "tool": tool_name,
                "arguments": arguments
            }

        try: 
            result = self.tools[tool_name](**arguments)

            return {
                "status": "EXECUTED",
                "tool": tool_name,
                "result": result
            }

        except (TypeError, ValueError):
            return {
                "status": "EXECUTION_ERROR",
                "tool": tool_name,
                "reason": "Invalid tool arguments"
            }

        except Exception:
            return {
                "status": "EXECUTION_ERROR",
                "tool": tool_name,
                "reason": "Tool execution failed"
            }