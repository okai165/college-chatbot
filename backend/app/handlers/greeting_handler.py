def handle_greeting(query):

    greetings = {

        "hi": "Hi! 👋 How can I help you?",

        "hello": "Hello! 👋 How can I help you?",

        "hey": "Hey! 😊 How can I assist you?",

        "hiya": "Hi! 😊",

        "yo": "Hey! 😊",

        "good morning":
        "Good morning! ☀️ How can I help you today?",

        "good afternoon":
        "Good afternoon! 😊 How can I assist you?",

        "good evening":
        "Good evening! 🌙 How can I help you?",

        "good night":
        "Good night! 🌙",

        "salam":
        "Wa Alaikum Assalam! 😊",

        "asalamualaikum":
        "Wa Alaikum Assalam! 😊",

        "assalamualaikum":
        "Wa Alaikum Assalam! 😊",

        "welcome":
        "Thank you! 😊 How can I help you?",

        "hey assistant":
        "Hello! 😊 How can I assist you?",

        "hi assistant":
        "Hello! 😊 How can I assist you?"

    }


    # Exact match first
    if query in greetings:
        return greetings[query]


    # Allow greeting + small extra words
    words = query.split()

    if len(words) <= 3:

        for key, response in greetings.items():

            key_words = key.split()

            # match only at beginning
            if words[:len(key_words)] == key_words:
                return response


    return None