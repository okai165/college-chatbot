from app.services.llm import generate_llm_response

def clean_text_llm(text: str):
    prompt = f"""
Clean this document text.
Remove navigation, headers, duplicates.

Return only meaningful content.

TEXT:
{text[:4000]}
"""
    return generate_llm_response(prompt).strip()