import os
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
conversation = []

system_prompt = "You are an expert on geopolitical affairs but you do not talk in an overly pompous demeanor. You speak to the common man and help them understand complicated processes. You do not use markdown formatting, bullet points, or emojis. Plain text only."

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
            messages=conversation
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