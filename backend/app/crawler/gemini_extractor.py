import json
import re
from app.services.llm import generate_llm_response


def extract_notification_data(text: str):

    prompt = f"""
You are a college notification analyzer.

Extract structured information from the document.

Return ONLY valid JSON. No explanations. No markdown.

Schema:
{{
    "title": "",
    "category": "",
    "summary": "",
    "start_date": "",
    "last_date": "",
    "eligibility": "",
    "required_documents": []
}}

Document:
{text[:8000]}
"""

    response = generate_llm_response(prompt)

    json_text = response.strip()

    # -----------------------------
    # Clean markdown wrappers if model adds them
    # -----------------------------
    json_text = re.sub(r"```json", "", json_text)
    json_text = re.sub(r"```", "", json_text).strip()

    # -----------------------------
    # Extract only JSON block (safe parsing)
    # -----------------------------
    try:
        return json.loads(json_text)

    except json.JSONDecodeError:
        # fallback: try to extract first JSON object
        match = re.search(r"\{.*\}", json_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))

        raise ValueError("LLM did not return valid JSON")