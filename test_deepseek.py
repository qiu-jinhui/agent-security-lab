import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com"
    )
)

response = client.chat.completions.create(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-flash"),
    messages=[
        {
            "role": "system",
            "content": "You are a helpful enterprise assistant."
        },
        {
            "role": "user",
            "content": "Explain what an AI Agent is in 3 sentences."
        }
    ],
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)

print("===== DEEPSEEK RESPONSE =====")
print(response.choices[0].message.content)

print("\n===== TOKEN USAGE =====")
print(response.usage)
