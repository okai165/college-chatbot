from app.services.llm import generate_llm_response

import json
import time
import re



# =========================
# METADATA ENRICHMENT
# =========================

def enrich_with_metadata(result: dict):

    result.setdefault("intent", "general")
    result.setdefault("subject", "")
    result.setdefault("keywords", [])
    result.setdefault("operation", None)
    result.setdefault("semester", None)
    result.setdefault("exam_type", None)


    query_text = (
        result.get("subject", "")
        + " "
        + " ".join(result.get("keywords", []))
    ).lower()



    # Semester extraction

    sem_match = re.search(
        r'(?:semester|sem)\s*(\d+)',
        query_text
    )


    if sem_match:

        result["semester"] = sem_match.group(1)



    # Exam type extraction

    if "internal" in query_text:

        result["exam_type"] = "internal"


    elif (
        "external" in query_text
        or "semester end" in query_text
    ):

        result["exam_type"] = "external"



    return result





# =========================
# QUERY ANALYZER
# =========================

def analyze_query(query):


    prompt = f"""

You are a query analysis engine for a college chatbot.


Analyze the student's question.


Extract ONLY JSON fields:


1. intent

2. subject

3. operation

4. keywords



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


For faculty queries:

Detect operation:

teacher:
Questions asking for teacher/faculty/person.

Examples:
- who teaches python
- teacher of python
- faculty for python
- who handles chemistry
- who is taking this subject
- who is the instructor


room:
Questions asking location.

Examples:
- where is python class
- room of chemistry
- lab for java
- location of ML class
- where does the teacher teach


time:
Questions asking timing/schedule.

Examples:
- when is python class
- what is the time of chemistry
- chemistry timing
- class timing
- lecture time
- when scheduled
- what time is the class


schedule:
Questions asking full timetable.

Examples:
- python schedule
- chemistry timetable
- complete class schedule

Examples:



Question:
Who teaches Python?


Output:

{{
"intent":"faculty",
"subject":"python",
"operation":"teacher",
"keywords":["python"]
}}



Question:
Where is Java class?


Output:

{{
"intent":"faculty",
"subject":"java",
"operation":"room",
"keywords":["java"]
}}



Question:
When is Machine Learning class?


Output:

{{
"intent":"faculty",
"subject":"machine learning",
"operation":"time",
"keywords":["machine learning"]
}}



Question:

{query}



Return JSON ONLY.

"""



    for attempt in range(3):

        try:


            response = generate_llm_response(
                prompt
            ).strip()



            # Remove markdown formatting

            if response.startswith("```"):

                response = (
                    response
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )



            # Extract JSON object

            start = response.find("{")

            end = response.rfind("}")


            if start != -1 and end != -1:

                response = response[
                    start:end+1
                ]



            result = json.loads(
                response
            )



            result = enrich_with_metadata(
                result
            )



            print(
                "\n========== QUERY ANALYZER =========="
            )

            print(result)

            # Faculty keyword fallback

            faculty_words = [
                "teacher",
                "teaches",
                "faculty",
                "handles",
                "instructor",
                "timing",
                "schedule",
                "scheduled",
                "lecture",
                "class time",
                "room",
                "lab",
                "where"
            ]


            query_lower = query.lower()


            if any(word in query_lower for word in faculty_words):

                if result["intent"] == "general":

                    result["intent"] = "faculty"


            if not result.get("operation"):

                if any(
                    x in query_lower
                    for x in [
                        "who",
                        "teacher",
                        "faculty",
                        "handles",
                        "instructor"
                    ]
                ):
                    result["operation"] = "teacher"


                elif any(
                    x in query_lower
                    for x in [
                        "where",
                        "room",
                        "lab",
                        "location"
                    ]
                ):
                    result["operation"] = "room"


                elif any(
                    x in query_lower
                    for x in [
                        "when",
                        "time",
                        "timing",
                        "schedule",
                        "scheduled"
                    ]
                ):
                    result["operation"] = "time"

            return result



        except Exception as e:


            print(
                f"QUERY ANALYZER RETRY {attempt+1}/3 FAILED:",
                e
            )


            time.sleep(1)





    # =========================
    # FALLBACK
    # =========================

    print(
        "\n========== QUERY ANALYZER FALLBACK =========="
    )


    return {

        "intent": "general",

        "subject": "",

        "operation": None,

        "keywords": [],

        "semester": None,

        "exam_type": None

    }