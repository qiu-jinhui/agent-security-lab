import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

MODEL = os.getenv("DEEPSEEK_MODEL")

def get_weather(city: str):
    return {
        "city": city,
        "temperature": 25,
        "condition": "Sunny"
    }

def get_air_quality(city: str):
    return {
        "city": city,
        "aqi": 165,
        "status": "Unhealthy"
    }

TOOLS = {
    "get_weather": get_weather,
    "get_air_quality": get_air_quality
}

TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string"
                    }
                },
                "required": ["city"]
            }

        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_air_quality",
            "description": "Get air quality information",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

def run_agent(user_input):

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use tools when necessary. "
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

            arguments = json.loads(
                call.function.arguments
            )

            print(f"[TOOL CALL] {name}: {arguments}")

            if name not in TOOLS:
                result = {"error": "Unknown tool"}
            else:
                try:
                    result = TOOLS[name](**arguments)
                except (TypeError, ValueError) as exc:
                    result = {"error": str(exc)}

            print(f"[TOOL RESULT] {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)
            })

    return "Maximum agent steps reached. "

if __name__ == "__main__":

    answer = run_agent(
        "What is the weather and air quality in Tokyo?"
        "Should I bring a mask? "
    )

    print("\n===== FINAL ANSWER =====")
    print(answer)