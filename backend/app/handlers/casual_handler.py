def handle_casual_query(query):

    casual = {

        "how are you":
        "I am doing great! 😊 I am here to help you.",

        "how r u":
        "I am doing good! 😊",

        "are you okay":
        "Yes, I am perfectly fine! 😊",

        "are you ok":
        "Yes! I am okay 😊",

        "you okay":
        "Yes, I am good! 😊",

        "what are you doing":
        "I am helping students with college information. 😊",

        "what's up":
        "I am here and ready to help! 😊",

        "whats up":
        "I am here and ready to help! 😊",

        "who are you":
        "I am the Government College for Women AI Assistant.",

        "what is your name":
        "I am the GCW AI Assistant. 😊",

        "tell me about yourself":
        "I help students with admissions, courses, notices, fees and college information.",

        "what can you do":
        "I can help with admission, courses, faculty, notices and other college information.",

        "can you help me":
        "Of course! 😊 Tell me your question.",

        "help":
        "Sure! 😊 What information do you need?",

        "are you there":
        "Yes! 😊 I am here.",

        "hello there":
        "Hello! 😊 How can I help?",

        "hey there":
        "Hey! 😊 What can I do for you?",

        "nice to meet you":
        "Nice to meet you too! 😊",

        "good job":
        "Thank you! 😊"

    }


    for key,value in casual.items():

        if key in query:
            return value


    return None