from app.services.llm import generate_llm_response
import json
import time
import re

def enrich_with_metadata(result: dict):
    query_text = (result.get("subject", "") + " " + " ".join(result.get("keywords", []))).lower()

    sem_match = re.search(r'(?:semester|sem)\s*(\d+)', query_text)
    if sem_match:
        result["semester"] = sem_match.group(1)

    if "internal" in query_text:
        result["exam_type"] = "internal"
    elif "external" in query_text or "semester end" in query_text:
        result["exam_type"] = "external"

    return result


def analyze_query(query):
    prompt = f"""
You are a query analysis engine for a college chatbot.

Analyze the student's question.

Extract:

1. intent
2. subject
3. keywords

Allowed intents:

- faculty
- admission
- fee
- scholarship
- timetable
- exam
- notice
- department
- course
- policy
- grievance
- examination
- library
- hostel
- iqac
- nirf
- ncc
- entrepreneurship
- innovation
- general

Question:

{query}

Return JSON ONLY.
"""

    for attempt in range(3):
        try:
            text = generate_llm_response(prompt).strip()

            # Remove markdown wrapper
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()

            start = text.find("{")
            end = text.rfind("}")

            if start != -1 and end != -1:
                text = text[start:end + 1]

            result = json.loads(text)

            result = enrich_with_metadata(result)

            print("\n========== QUERY ANALYZER ==========")
            print(result)

            return result

        except Exception as e:
            print(f"QUERY ANALYZER RETRY {attempt + 1}/3 FAILED:", e)
            time.sleep(1)

    print("\n========== QUERY ANALYZER FALLBACK ==========")
    return {
        "intent": "general",
        "subject": "",
        "keywords": [],
        "semester": None,
        "exam_type": None
    }