import os
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

# Read the file
filename = input("Enter filename to analyze: ")
filepath = os.path.join(os.path.dirname(__file__), filename)
with open(filepath, "r") as f:
    data = f.read()

print("File loaded. Sending to Claude for analysis...\n")

# Send to Claude
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a mainframe operations analyst. You give concise, professional analysis. No markdown, no bullets, no emojis. Plain text only.",
    messages=[
        {"role": "user", "content": f"Analyze this operations report and give me a brief summary of the key issues and recommended actions:\n\n{data}"}
    ]
)

print("Claude's Analysis:")
print(response.content[0].text)
# Save the analysis
with open("analysis_output.txt", "w") as f:
    f.write(response.content[0].text)

print("\nAnalysis saved to analysis_output.txt")