from app.services.llm import client
import json


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

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown wrapper if Gemini returns it
        if text.startswith("```json"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        result = json.loads(text)

        print("\n========== QUERY ANALYZER ==========")
        print(result)

        return result

    except Exception as e:

        print("QUERY ANALYZER ERROR:", e)

        return {
            "intent": "general",
            "subject": "",
            "keywords": []
        }