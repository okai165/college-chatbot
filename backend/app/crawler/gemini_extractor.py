import json

from app.services.llm import client

def extract_notification_data(text):

    prompt = f"""
You are a college notification analyzer.

Extract information from the document.

Return ONLY valid JSON.

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    json_text = response.text.strip()

    if json_text.startswith("```json"):
        json_text = json_text.replace("```json", "")
        json_text = json_text.replace("```", "")

    return json.loads(json_text)