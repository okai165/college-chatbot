def handle_farewell(query):

    farewells = {

        "bye": "Goodbye! 👋 Have a great day.",
        "goodbye": "Goodbye! 👋 Take care.",
        "see you": "See you! 😊",
        "see ya": "See you! 👋",
        "see u": "See you! 😊",

        "later": "See you later! 😊",
        "talk later": "Sure! 😊",
        "talk to you later": "Sure! 😊",

        "catch you later": "See you! 👋",
        "until next time": "See you again! 😊",

        "good night": "Good night! 🌙",
        "night": "Good night! 🌙",

        "have a good day": "Thank you! You too 😊",
        "have a nice day": "Thank you! 😊",

        "i am leaving": "Okay! Take care 😊",
        "i have to go": "No problem! See you 😊",
        "gotta go": "Alright! See you later 👋",

    }


    return farewells.get(query)