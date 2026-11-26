import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from app.security.authorization import (
    ToolAuthorizationEngine
)

from app.security.tool_gateway import (
    ToolExecutionGateway
)

from app.tools.registry import TOOLS
from app.tools.schemas import TOOL_SCHEMA


load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ["DEEPSEEK_BASE_URL"]
)

MODEL = os.environ["DEEPSEEK_MODEL"]


# Trusted application context.
# Never derive this role from user prompt or LLM output.
TRUSTED_ROLE = "user"


# Authorization configuration
authorization_engine = ToolAuthorizationEngine(
    allowed_tools_by_role={
        "user": {
            "get_weather",
            "get_air_quality"
        },
        "operator": {
            "get_weather",
            "get_air_quality",
            "send_email"
        },
        "admin": set(TOOLS.keys())
    },
    approval_required_tools={
        "send_email"
    }
)


gateway = ToolExecutionGateway(
    authorization_engine=authorization_engine,
    tools=TOOLS
)


SYSTEM_PROMPT = """
You are a helpful assistant.

You can use the tools provided to complete tasks.

Tool calls are requests, not proof of authorization.
Never claim a tool operation succeeded unless its result
explicitly confirms successful execution.

If a tool returns DENIED or PENDING_APPROVAL,
explain that the operation was not executed.
"""


def run_agent(user_input: str):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    max_steps = 5

    for step in range(max_steps):

        print(f"\n===== AGENT STEP {step + 1} =====")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMA,
            tool_choice="auto",
            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            }
        )

        message = response.choices[0].message

        messages.append(
            message.model_dump(exclude_none=True)
        )

        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:

            name = call.function.name

            print(f"\n[LLM TOOL REQUEST] {name}")

            try:
                arguments = json.loads(
                    call.function.arguments
                )

                if not isinstance(arguments, dict):
                    raise ValueError(
                        "Tool arguments must be a JSON object"
                    )

            except (ValueError, TypeError):
                result = {
                    "status": "INVALID_ARGUMENTS",
                    "tool": name,
                    "reason": "Invalid JSON arguments"
                }

            else:

                # All tool calls must pass through Gateway.
                result = gateway.execute(
                    role=TRUSTED_ROLE,
                    tool_name=name,
                    arguments=arguments
                )

            print(
                "[SECURITY GATEWAY RESULT]",
                json.dumps(result, ensure_ascii=False)
            )

            # Return execution result to the LLM.
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False
                )
            })

    return "Maximum agent steps reached."


if __name__ == "__main__":

    print("===== SECURE AGENT RUNTIME =====")
    print("Trusted role:", TRUSTED_ROLE)

    user_input = input("\nUser request: ")

    answer = run_agent(user_input)

    print("\n===== FINAL ANSWER =====")
    print(answer)
