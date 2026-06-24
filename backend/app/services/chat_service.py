from sqlalchemy import text
from app.db.database import engine
from app.rag.retriever import retrieve_similar_chunks
from app.services.llm import client
from sqlalchemy import text
from app.rag.notification_retriever import search_notifications
from app.rag.keyword_search import keyword_search
from app.rag.query_analyzer import analyze_query
from app.rag.subject_aliases import SUBJECT_ALIASES
import time
import re 

# Store last faculty subject per session
last_subject_by_session = {}
# =========================
# CHAT MEMORY
# =========================
def get_chat_history(session_id, limit=3):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT role, message
                FROM chat_history
                WHERE session_id = :session_id
                ORDER BY id DESC
                LIMIT :limit
            """),
            {
                "session_id": session_id,
                "limit": limit
            }
        )

        rows = result.fetchall()

    return rows[::-1]

# =========================
# QUERY REWRITER
# =========================
def rewrite_query(user_query, history):

    memory_text = "\n".join(
        [f"{h.role}: {h.message}" for h in history]
    ) if history else ""

    prompt = f"""
You are a query rewriting assistant.

Your job is to convert follow-up questions into complete standalone questions.

Examples:

Conversation:
user: who teaches python
assistant: python is taught by prof rashid ashraf

User:
where

Standalone Question:
where is the python class held?

Conversation:
user: who teaches python
assistant: python is taught by prof rashid ashraf

User:
when

Standalone Question:
when is the python class scheduled?

Conversation:
user: tell me the dress code
assistant: students must wear uniforms

User:
and what about boys

Standalone Question:
what is the boys uniform according to the college dress code?

Conversation:
{memory_text}

User:
{user_query}

Standalone Question:
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        rewritten_query = response.text.strip()

        print("\n========== REWRITTEN QUERY ==========")
        print(rewritten_query)

        return rewritten_query

    except Exception:
        return user_query
def classify_intent(query: str) -> str:
    query = query.lower()

    if any(x in query for x in ["can i wear", "allowed", "dress code", "uniform"]):
        return "policy"
    
    if any(x in query for x in ["who teaches", "faculty", "teacher"]):
        return "faculty"
    
    if any(x in query for x in ["where", "when", "time", "room"]):
        return "schedule"
    
    return "general"  
def handle_policy_query(query, docs):
    context = "\n".join([d.content for d in docs if d.content])

    prompt = f"""
You are a college policy validation assistant.

Extract rules from the context and answer clearly.

Context:
{context}

Question:
{query}

Rules:
- If the action is not allowed → explicitly say Verdict: NOT ALLOWED and explain why, referencing the policy
- If the action is allowed → explicitly say Verdict: ALLOWED and explain why, referencing the policy
- If unclear → say not found
- Always provide a short explanation based on the policy instead of only saying ALLOWED/NOT ALLOWED
- Format the answer as:
  Verdict: ALLOWED/NOT ALLOWED
  Policy Reference: <short explanation from context>
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

# =========================
# FACULTY SEARCH
# =========================
def search_faculty(query: str):
    query = query.strip().lower()

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    faculty_name,
                    subject_name,
                    time_slot,
                    room_number
                FROM faculty_schedule
                WHERE
                    LOWER(subject_name) LIKE :like_query
                    OR LOWER(faculty_name) LIKE :like_query
                LIMIT 5
            """),
            {
                "like_query": f"%{query}%"
            }
        )
        return result.fetchall()


def clean_faculty_query(rewritten_query: str) -> str:
    query = rewritten_query.lower()
    # Remove filler words but keep subject keywords intact
    remove_words = [
        "who", "teaches", "teach", "teacher", "faculty",
        "of", "what", "when", "where", "is", "the", "class",
        "room", "classroom", "timing", "time", "schedule",
        "for", "at", "in"
    ]
    for word in remove_words:
        query = re.sub(rf"\b{word}\b", " ", query)

    query = re.sub(r"[^\w\s]", "", query)  # remove punctuation
    query = " ".join(query.split())        # normalize spaces
    return query.strip()

# =========================
# SUBJECT NORMALIZER
# =========================

def normalize_subject(subject):

    if not subject:
        return ""

    subject = subject.lower().strip()


    return SUBJECT_ALIASES.get(subject, subject)
# =========================
# MAIN RAG FUNCTION
# =========================
def generate_response(user_query, session_id):
    query = user_query.lower().strip()
    intent = classify_intent(user_query)

    # Handle follow-up questions
    history = get_chat_history(session_id)
    rewritten_query = rewrite_query(user_query, history)

    # Analyze query
    analysis = analyze_query(rewritten_query)

    intent = analysis.get("intent", "general")
    subject = analysis.get("subject", "")
    keywords = analysis.get("keywords", [])
    
    print("\n========== QUERY ANALYSIS ==========")
    print(analysis)
    
    # Greetings
    if query in ["hi", "hello", "hey"]:
        return "Hello! 👋 Welcome to the College Information Assistant. How can I help you today?"
    if query == "how are you":
        return "I'm doing well. How can I assist you today?"
    if query in ["thanks", "thank you"]:
        return "You're welcome! 😊"
    if query in ["bye", "goodbye"]:
        return "Goodbye! Have a great day."

    # =========================
    # RETRIEVE DOCUMENTS
    # =========================

    docs = retrieve_similar_chunks(
    rewritten_query + " " + subject
    )

    keyword_docs = keyword_search(
        " ".join(keywords)
    )
    docs.extend(keyword_docs)
    notifications = []

    admission_keywords = [
        "admission",
        "eligibility",
        "fee",
        "fees",
        "fyug",
        "honours",
        "honors",
        "intake",
        "seat",
        "notification",
        "notice",
        "course"
    ]

    if any(
        keyword in rewritten_query.lower()
        for keyword in admission_keywords
    ):
        notifications = search_notifications()

    # =========================
    # FACULTY SEARCH
    # =========================
    clean_query = subject if subject else clean_faculty_query(rewritten_query)
    
    clean_query = normalize_subject(clean_query)
    
    followup_words = ["where", "when", "time", "timing", "at what time", "room", "classroom"]

    # If it's a follow-up but we don't have a subject stored, return fallback immediately
    if any(word in query for word in followup_words) and session_id not in last_subject_by_session:
        return "Sorry, I cannot find relevant information in the college documents."

    # If it's a follow-up and we DO have a subject stored, reuse it
    if any(word in query for word in followup_words) and session_id in last_subject_by_session:
        clean_query = last_subject_by_session[session_id]

    faculty_rows = search_faculty(clean_query) if clean_query else []
    row = faculty_rows[0] if faculty_rows else None

    faculty_context = ""
    if row:
        last_subject_by_session[session_id] = row.subject_name.lower()
        if "who teaches" in query or "teacher" in query or "faculty" in query:
            return f"{row.subject_name} is taught by {row.faculty_name}."
        elif "time" in query or "when" in query or "timing" in query or "at what time" in query:
            return f"{row.subject_name} class is scheduled from {row.time_slot}."
        elif "room" in query or "where" in query or "classroom" in query:
            return f"{row.subject_name} class is held in {row.room_number}."
        else:
            return f"""
    Faculty Name: {row.faculty_name}
    Subject: {row.subject_name}
    Time Slot: {row.time_slot}
    Room Number: {row.room_number}
    """


    # =========================
    # BUILD DOCUMENT CONTEXT
    # =========================
    notification_context = ""

    for n in notifications:

        notification_context += f"""
    Title: {n.title}

    Summary: {n.summary}

    Eligibility: {n.eligibility}

    Start Date: {n.start_date}

    Last Date: {n.last_date}

    -----------------------
    """
    context_chunks = []
    for i, row in enumerate(docs):
        if row.content:
            cleaned = row.content.strip()
            if cleaned:
                # Include distance score for relevance weighting
                context_chunks.append(
                    f"[Chunk {i+1} | distance={row.distance:.4f}] {cleaned}"
                )

    if not context_chunks and not faculty_rows:
        return "Sorry, I cannot find relevant information in the college documents."

    # Limit context length (truncate if > 12000 chars)
    document_context = "\n\n".join(context_chunks)
    if len(document_context) > 12000:
        document_context = document_context[:12000] + "\n...[truncated]"

    context = f"""
    COLLEGE DOCUMENTS:

    {faculty_context}

    {document_context}

    ADMISSION NOTIFICATIONS:

    {notification_context}
    """

    # =========================
    # CHAT MEMORY
    # =========================
    history = get_chat_history(session_id)
    memory_text = "\n".join([f"{h.role}: {h.message}" for h in history]) if history else ""

    # =========================
    # STRICT PROMPT
    # =========================
    prompt = f"""
You are an AI assistant for Government College for Women M.A. Road Srinagar.

Answer using the provided context.

Rules:

- Use information from retrieved documents.
- Combine information from multiple documents if needed.
- Answer naturally.
- If partial information exists, provide the available information.
- Only say:

Sorry, I cannot find relevant information in the college documents.

when the answer is not present anywhere in the context.

CHAT HISTORY:
{memory_text}

CONTEXT:
{context}

QUESTION:
{user_query}
"""

    print("\n========== SENDING TO GEMINI ==========\n")

    # =========================
    # GEMINI RESPONSE WITH RETRY
    # =========================
    for attempt in range(3):
        try:
            print("Gemini API call started")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            print("\n========== GEMINI RESPONSE ==========\n")
            print(response.text)
            return response.text
        except Exception as e:
            print(f"\n❌ RETRY {attempt + 1}/3")
            import traceback
            traceback.print_exc()
            time.sleep(2)

    return "AI service is temporarily busy. Please try again in a few seconds."

