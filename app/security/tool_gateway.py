
from app.security.authorization import (
    ToolAuthorizationEngine
)

from app.security.argument_validator import (
    ToolArgumentValidator,
    ArgumentValidationError
)

from app.security.context import ExecutionContext


class ToolExecutionGateway:

    def __init__(
        self,
        authorization_engine: ToolAuthorizationEngine,
        tools: dict,
        argument_schemas: dict,
        resource_authorizer=None,
        resource_protected_tools=None
    ):

        self.authorization_engine = authorization_engine
        self.tools = tools
        self.argument_schemas = argument_schemas

        self.argument_validator = ToolArgumentValidator()

        self.resource_authorizer = resource_authorizer

        self.resource_protected_tools = (
            resource_protected_tools or set()
        )

    def execute(
        self,
        role: str | None,
        tool_name: str,
        arguments: dict,
        context: ExecutionContext | None = None
    ) -> dict:

        # 1. Trusted identity consistency
        if context is not None and role != context.role:
            return {
                "status": "DENIED",
                "reason": "Role does not match execution context"
            }

        effective_role = (
            context.role if context is not None else role
        )

        # 2. RBAC
        decision = self.authorization_engine.authorize(
            role=effective_role,
            tool_name=tool_name,
            registered_tools=set(self.tools.keys())
        )

        if decision.action == "DENY":
            return {
                "status": "DENIED",
                "reason": decision.reason,
                "tool": tool_name
            }

        # 3. Argument validation
        try:
            self.argument_validator.validate(
                tool_name=tool_name,
                arguments=arguments,
                schemas=self.argument_schemas
            )

        except ArgumentValidationError as exc:
            return {
                "status": "INVALID_ARGUMENTS",
                "reason": str(exc),
                "tool": tool_name
            }

        # 4. Resource authorization
        if tool_name in self.resource_protected_tools:

            if self.resource_authorizer is None:
                return {
                    "status": "DENIED",
                    "reason": "Resource authorization is not configured",
                    "tool": tool_name
                }

            resource_id = arguments.get("customer_id")

            if not self.resource_authorizer.authorize(
                context=context,
                resource_id=resource_id
            ):
                return {
                    "status": "DENIED",
                    "reason": "Resource access denied",
                    "tool": tool_name
                }

        # 5. Human approval
        if decision.action == "REQUIRE_APPROVAL":
            return {
                "status": "PENDING_APPROVAL",
                "reason": decision.reason,
                "tool": tool_name,
                "arguments": arguments
            }

        # 6. Execute
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
