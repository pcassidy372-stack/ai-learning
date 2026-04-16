import os
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
conversation = []

print("=== ChatBot V1 ===")
print("Type 'quit' to exit\n")

persona = input("What kind of assistant do you want? (e.g. mainframe expert, geopolitical analyst, fitness coach): ")
system_prompt = f"You are a {persona}. You speak clearly and concisely. No markdown formatting, bullet points, or emojis. Plain text only."

print(f"\nAssistant ready as: {persona}\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    if not user_input.strip():
        print("Please type something first.\n")
        continue

    conversation.append({"role": "user", "content": user_input})

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=conversation,
        )
        reply = response.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        print(f"Claude: {reply}\n")

    except anthropic.APIConnectionError:
        print("Connection error. Check your internet and try again.\n")
    except anthropic.RateLimitError:
        print("Rate limit hit. Wait a moment and try again.\n")
    except anthropic.APIStatusError as e:
        print(f"API error {e.status_code}: {e.message}\n")