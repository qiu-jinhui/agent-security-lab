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

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

messages = [
    {
        "role": "user",
        "content": "What is the weather in Tokyo?"
    }
]

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto",
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)

message = response.choices[0].message

print("===== LLM RESPONSE =====")
print(message)

if message.tool_calls: 

    for tool_call in message.tool_calls:

        function_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        print("\n===== TOOL CALL =====")
        print(f"Function: {function_name}")
        print(f"Arguments: {arguments}")

        if function_name == "get_weather":
            result = get_weather(**arguments)
        else:
            result = {"error": "Unknown function"}

        print("\n===== TOOL RESULT =====")
        print(result)

else:
    print("LLM did not request a tool. ")