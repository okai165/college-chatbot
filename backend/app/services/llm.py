from openai import OpenAI
from app.core.config import LLM_API_KEY, LLM_BASE_URL

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

MODEL = "opencode/deepseek-v4-flash-free"


def generate_llm_response(prompt: str):
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content