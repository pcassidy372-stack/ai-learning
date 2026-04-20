import os
import csv
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

# Read the CSV file
filepath = os.path.join(os.path.dirname(__file__), "sample_data.csv")
rows = []

with open(filepath, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Quick stats before sending to Claude
total = len(rows)
failed = sum(1 for row in rows if row['status'] == 'failed')
breaches = sum(1 for row in rows if row['sla_breach'] == 'yes')

print(f"Total jobs: {total}")
print(f"Failed jobs: {failed}")
print(f"SLA breaches: {breaches}")
print("\nSending to Claude for analysis...\n")

# Format data for Claude
data_str = "\n".join([str(row) for row in rows])

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a mainframe operations analyst. No markdown, no bullets, no emojis. Plain text only.",
    messages=[
        {"role": "user", "content": f"Analyze this job execution data and identify patterns and recommendations:\n\n{data_str}"}
    ]
)

print("Claude's Analysis:")
print(response.content[0].text)