from app.services.chat_service import generate_response

response = generate_response(
    "What is cloud computing?"
)

print(response)