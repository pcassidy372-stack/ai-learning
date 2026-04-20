import os
import csv
import json
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

print("=== Mainframe Operations Report Generator ===\n")

# Read CSV data
filepath = os.path.join(os.path.dirname(__file__), "sample_data.csv")
rows = []

with open(filepath, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Calculate stats
total = len(rows)
failed = sum(1 for row in rows if row['status'] == 'failed')
breaches = sum(1 for row in rows if row['sla_breach'] == 'yes')
success_rate = round(((total - failed) / total) * 100, 1)

print(f"Data loaded: {total} jobs analyzed")
print(f"Generating report...\n")

# Format data for Claude
data_str = "\n".join([str(row) for row in rows])

# Generate report with Claude
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=2048,
    system="""You are a chief of staff preparing an executive briefing for the head of mainframe operations at a large fintech company. 
Write in a professional, concise style suitable for a senior executive. 
No markdown formatting, no bullets, no emojis. Plain text only.
Structure your report with clear sections: Executive Summary, Key Findings, Risk Areas, and Recommended Actions.""",
    messages=[
        {"role": "user", "content": f"""Generate an executive operations report based on this job execution data.

Key statistics:
- Total jobs: {total}
- Failed jobs: {failed}
- SLA breaches: {breaches}
- Success rate: {success_rate}%

Raw data:
{data_str}

Write this as a briefing for the head of mainframe operations."""}
    ]
)

report = response.content[0].text

# Save report with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"ops_report_{timestamp}.txt"
output_filepath = os.path.join(os.path.dirname(__file__), output_filename)

with open(output_filepath, "w") as f:
    f.write(f"MAINFRAME OPERATIONS REPORT\n")
    f.write(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n")
    f.write("=" * 50 + "\n\n")
    f.write(report)

print("Report generated successfully.")
print(f"Saved as: {output_filename}\n")
print(report)