import os
from anthropic import Anthropic

client = Anthropic()
conversation = []

system_prompt = "You are an adept handicapper of horse racing. You reference past performances, track records and other relevant information to help you make your picks.You do not use markdown formatting, bullet points, or emojis. Plain text only."

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    if not user_input.strip():
        print("Please type something first.\n")
        continue
    
    conversation.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=conversation
    )
    
    reply = response.content[0].text
    conversation.append({"role": "assistant", "content": reply})
    
    print(f"Claude: {reply}\n")