def handle_acknowledgement(query):

    acknowledgements = {

        "ok": "Great! 😊 Let me know if you need anything else.",
        "okay": "Alright! 😊 Feel free to ask more.",
        "okey": "Alright! 😊",
        "kk": "Okay! 😊",
        "k": "Alright! 😊",
        "yes": "Great! 😊 How can I help you?",
        "yeah": "Great! 😊",
        "yep": "Perfect! 😊",
        "yup": "Alright! 😊",
        "ya": "Okay! 😊",
        "y": "Sure! 😊",

        "alright": "Perfect! 😊",
        "fine": "Great! 😊",
        "good": "Nice! 😊",
        "great": "Glad to help! 😊",
        "awesome": "Thank you! 😊",
        "amazing": "Happy to help! 😊",
        "perfect": "Excellent! 😊",
        "excellent": "Thank you! 😊",

        "nice": "Thank you! 😊",
        "cool": "Great! 😄",
        "awesome": "Glad you liked it! 😊",

        "got it": "Perfect! 👍",
        "gotcha": "Great! 👍",
        "understood": "Good! 😊",
        "i understand": "Great! 😊",
        "clear": "Perfect! 😊",
        "makes sense": "Glad it helped! 😊",

        "done": "Great! ✅",
        "finished": "Awesome! ✅",
        "complete": "Perfect! ✅",

        "lets go": "Sure! 🚀 How can I help?",
        "let's go": "Sure! 🚀",

        "sure": "Great! 😊",
        "okay sure": "Alright! 😊",
        "yes please": "Sure! 😊",

        "hmm": "I am here if you need anything. 😊",
        "hmmm": "Take your time! 😊",
        "emm": "No problem! 😊",
        "umm": "I am here to help. 😊",

        "lol": "😊 Happy to help!",
        "haha": "😊",

        "oh": "Yes? 😊",
        "oh okay": "Alright! 😊"

    }


    return acknowledgements.get(query)