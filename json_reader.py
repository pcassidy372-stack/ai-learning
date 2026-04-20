import os
import json
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

# Read the JSON file
filepath = os.path.join(os.path.dirname(__file__), "sample_data.json")
with open(filepath, "r") as f:
    data = json.load(f)

# Access individual fields
print(f"Report date: {data['report_date']}")
print(f"Failed jobs: {data['failed_jobs']}")
print(f"SLA breaches: {data['sla_breaches']}")
print("\nSending to Claude for analysis...\n")

# Convert back to string for Claude
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a mainframe operations analyst. No markdown, no bullets, no emojis. Plain text only.",
    messages=[
        {"role": "user", "content": f"Analyze this operations data and summarize key issues:\n\n{json.dumps(data, indent=2)}"}
    ]
)

print("Claude's Analysis:")
print(response.content[0].text)