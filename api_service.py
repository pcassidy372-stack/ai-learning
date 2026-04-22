import os
import csv
import anthropic
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()
app = FastAPI()

# Load data at startup
def load_ops_data():
    filepath = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    rows = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

ops_data = load_ops_data()

# Request model
class QuestionRequest(BaseModel):
    question: str

# Define tools
tools = [
    {
        "name": "get_overall_stats",
        "description": "Get overall operational statistics",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_failed_jobs",
        "description": "Get all failed jobs",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Tool implementations
def get_overall_stats():
    total = len(ops_data)
    failed = sum(1 for row in ops_data if row['status'] == 'failed')
    breaches = sum(1 for row in ops_data if row['sla_breach'] == 'yes')
    success_rate = round(((total - failed) / total) * 100, 1)
    return f"Total: {total}, Failed: {failed}, Breaches: {breaches}, Success Rate: {success_rate}%"

def get_failed_jobs():
    failed = [row for row in ops_data if row['status'] == 'failed']
    return "\n".join([f"Job {r['job_id']} - {r['domain']} - SLA breach: {r['sla_breach']}" for r in failed])

def process_tool_call(tool_name, tool_input):
    if tool_name == "get_overall_stats":
        return get_overall_stats()
    elif tool_name == "get_failed_jobs":
        return get_failed_jobs()

# Agent logic
def run_agent(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system="You are a mainframe operations assistant. Use your tools to answer questions accurately. No markdown, no bullets, no emojis. Plain text only.",
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        
        else:
            return next(block.text for block in response.content if hasattr(block, "text"))

# API endpoints
@app.get("/")
def root():
    return {"status": "Mainframe Operations Assistant is running"}

@app.get("/health")
def health():
    total = len(ops_data)
    failed = sum(1 for row in ops_data if row['status'] == 'failed')
    success_rate = round(((total - failed) / total) * 100, 1)
    return {
        "status": "healthy",
        "total_jobs": total,
        "success_rate": success_rate
    }

@app.post("/ask")
def ask(request: QuestionRequest):
    answer = run_agent(request.question)
    return {
        "question": request.question,
        "answer": answer
    }