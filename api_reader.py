import os
import json
import requests
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

# Fetch live data from a public API
print("Fetching live ISS position data...\n")
response = requests.get("http://api.open-notify.org/iss-now.json")
data = response.json()

print(f"Status: {data['message']}")
print(f"Latitude: {data['iss_position']['latitude']}")
print(f"Longitude: {data['iss_position']['longitude']}")
print(f"Timestamp: {data['timestamp']}")
print("\nSending to Claude...\n")

# Send to Claude
ai_response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a helpful assistant. No markdown, no bullets, no emojis. Plain text only.",
    messages=[
        {"role": "user", "content": f"The International Space Station is currently at these coordinates: {json.dumps(data, indent=2)}. Tell me what part of the world it is flying over right now and anything interesting about that location."}
    ]
)

print("Claude's Analysis:")
print(ai_response.content[0].text)