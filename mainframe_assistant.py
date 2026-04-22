import os
import csv
import anthropic
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# Load operational data at startup
def load_ops_data():
    filepath = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    rows = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

ops_data = load_ops_data()

# Calculate summary stats
def get_summary_stats(data):
    total = len(data)
    failed = sum(1 for row in data if row['status'] == 'failed')
    breaches = sum(1 for row in data if row['sla_breach'] == 'yes')
    success_rate = round(((total - failed) / total) * 100, 1)
    domains = list(set(row['domain'] for row in data))
    return {
        "total": total,
        "failed": failed,
        "breaches": breaches,
        "success_rate": success_rate,
        "domains": domains
    }

# Define tools
tools = [
    {
        "name": "get_overall_stats",
        "description": "Get overall operational statistics including total jobs, failures, and SLA breaches",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_domain_stats",
        "description": "Get statistics for a specific domain",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "The domain name to analyze e.g. CICS Region 4, DB2, IMS"
                }
            },
            "required": ["domain"]
        }
    },
    {
        "name": "get_failed_jobs",
        "description": "Get a list of all failed jobs",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_sla_breaches",
        "description": "Get all jobs that breached SLA",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "save_report",
        "description": "Save a report to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The report content to save"
                },
                "filename": {
                    "type": "string",
                    "description": "The filename to save as"
                }
            },
            "required": ["content", "filename"]
        }
    }
]

# Tool implementations
def get_overall_stats():
    stats = get_summary_stats(ops_data)
    return f"Total jobs: {stats['total']}, Failed: {stats['failed']}, SLA Breaches: {stats['breaches']}, Success Rate: {stats['success_rate']}%, Domains: {', '.join(stats['domains'])}"

def get_domain_stats(domain):
    domain_jobs = [row for row in ops_data if domain.lower() in row['domain'].lower()]
    if not domain_jobs:
        return f"No data found for domain: {domain}"
    total = len(domain_jobs)
    failed = sum(1 for row in domain_jobs if row['status'] == 'failed')
    breaches = sum(1 for row in domain_jobs if row['sla_breach'] == 'yes')
    avg_time = round(sum(float(row['completion_time_minutes']) for row in domain_jobs) / total, 2)
    return f"Domain: {domain}, Total: {total}, Failed: {failed}, Breaches: {breaches}, Avg completion time: {avg_time} min"

def get_failed_jobs():
    failed = [row for row in ops_data if row['status'] == 'failed']
    if not failed:
        return "No failed jobs found"
    result = []
    for job in failed:
        result.append(f"Job {job['job_id']} - {job['domain']} - {job['completion_time_minutes']} min - SLA breach: {job['sla_breach']}")
    return "\n".join(result)

def get_sla_breaches():
    breaches = [row for row in ops_data if row['sla_breach'] == 'yes']
    if not breaches:
        return "No SLA breaches found"
    result = []
    for job in breaches:
        result.append(f"Job {job['job_id']} - {job['domain']} - {job['completion_time_minutes']} min")
    return "\n".join(result)

def save_report(content, filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.txt"
    filepath = os.path.join(os.path.dirname(__file__), full_filename)
    with open(filepath, "w") as f:
        f.write(content)
    return f"Report saved as {full_filename}"

def process_tool_call(tool_name, tool_input):
    if tool_name == "get_overall_stats":
        return get_overall_stats()
    elif tool_name == "get_domain_stats":
        return get_domain_stats(tool_input["domain"])
    elif tool_name == "get_failed_jobs":
        return get_failed_jobs()
    elif tool_name == "get_sla_breaches":
        return get_sla_breaches()
    elif tool_name == "save_report":
        return save_report(tool_input["content"], tool_input["filename"])

# Agent loop with conversation memory
def run_agent(messages):
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            system="""You are an intelligent mainframe operations assistant for a large fintech company. 
You have access to tools that query live operational data. 
Use your tools to answer questions accurately. 
When asked for a report, use the save_report tool to save it.
No markdown formatting, no bullets, no emojis. Plain text only.""",
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [Using tool: {block.name}]")
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        else:
            final_response = next(block.text for block in response.content if hasattr(block, "text"))
            messages.append({"role": "assistant", "content": final_response})
            print(f"Assistant: {final_response}\n")
            break

    return messages

# Main conversation loop
print("=== Mainframe Operations Assistant ===")
print("Ask me anything about your operations data.")
print("Try: 'What is our current status?' or 'Show me all failed jobs'")
print("Type 'quit' to exit\n")

conversation = []

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    if not user_input.strip():
        continue

    conversation.append({"role": "user", "content": user_input})
    conversation = run_agent(conversation)