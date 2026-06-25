from app.services.llm import client
import json
import time
import re


def enrich_with_metadata(result: dict):
    """
    Adds semester and exam_type fields to analyzer result.
    """
    query_text = (result.get("subject", "") + " " + " ".join(result.get("keywords", []))).lower()

    # Semester detection (e.g., "10 sem", "semester 3rd")
    sem_match = re.search(r'(?:semester|sem)\s*(\d+)', query_text)
    if sem_match:
        result["semester"] = sem_match.group(1)

    # Exam type detection
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
- general

Question:

{query}

Return JSON ONLY.

Example 1:

Question:
Who teaches Artificial Intelligence?

Output:
{{
    "intent":"faculty",
    "subject":"Artificial Intelligence",
    "keywords":["Artificial Intelligence","faculty"]
}}

Example 2:

Question:
What is the fee for FYUG semester 7th?

Output:
{{
    "intent":"fee",
    "subject":"FYUG Semester 7th",
    "keywords":["fee","FYUG","Semester 7th"]
}}

Example 3:

Question:
How can I take admission in fourth year FYUG?

Output:
{{
    "intent":"admission",
    "subject":"Fourth Year FYUG",
    "keywords":["admission","FYUG","fourth year"]
}}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text.strip()

            # Remove markdown wrapper
            if text.startswith("```json"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            # Extract JSON safely
            start = text.find("{")
            end = text.rfind("}")

            if start != -1 and end != -1:
                text = text[start:end + 1]

            result = json.loads(text)

            # Enrich with semester/exam_type metadata
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
