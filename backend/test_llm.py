from openai import OpenAI

client = OpenAI(
    api_key="sk-duyOZXg9LQWydoE5w659AA",
    base_url="https://llm.app.emlylabs.com/v1"
)

response = client.chat.completions.create(
    model="opencode/deepseek-v4-flash-free",
    messages=[
        {
            "role": "user",
            "content": "Hello, reply with Connection successful"
        }
    ]
)

print(response.choices[0].message.content)