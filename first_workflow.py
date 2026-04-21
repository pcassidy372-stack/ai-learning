import os
import anthropic
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict

load_dotenv()

client = anthropic.Anthropic()

class WorkflowState(TypedDict):
    raw_data: str
    metrics: str
    success_rate: float
    analysis: str
    report: str
    alert: str

def load_data(state: WorkflowState) -> WorkflowState:
    print("Step 1: Loading data...")
    filepath = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    with open(filepath, "r") as f:
        state["raw_data"] = f.read()
    print("Data loaded.\n")
    return state

def calculate_metrics(state: WorkflowState) -> WorkflowState:
    print("Step 2: Calculating metrics...")
    lines = state["raw_data"].strip().split("\n")
    rows = [line.split(",") for line in lines[1:]]
    
    total = len(rows)
    failed = sum(1 for row in rows if row[2].strip() == "failed")
    breaches = sum(1 for row in rows if row[4].strip() == "yes")
    success_rate = round(((total - failed) / total) * 100, 1)
    
    state["success_rate"] = success_rate
    state["metrics"] = f"Total jobs: {total}, Failed: {failed}, SLA Breaches: {breaches}, Success Rate: {success_rate}%"
    print(f"Metrics: {state['metrics']}\n")
    return state

# Decision function - routes based on success rate
def route_by_severity(state: WorkflowState) -> str:
    if state["success_rate"] < 80:
        print("WARNING: Success rate below 80% - routing to critical alert path\n")
        return "critical"
    else:
        print("Success rate acceptable - routing to standard analysis\n")
        return "standard"

def send_critical_alert(state: WorkflowState) -> WorkflowState:
    print("Step 3A: Generating critical alert...")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system="You are a mainframe operations analyst. Write urgent alerts. No markdown, no bullets, no emojis. Plain text only.",
        messages=[{
            "role": "user",
            "content": f"Write a critical alert message for the operations team based on these metrics: {state['metrics']}"
        }]
    )
    state["alert"] = response.content[0].text
    state["analysis"] = response.content[0].text
    print("Critical alert generated.\n")
    return state

def analyze_data(state: WorkflowState) -> WorkflowState:
    print("Step 3B: Running standard analysis...")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system="You are a mainframe operations analyst. No markdown, no bullets, no emojis. Plain text only.",
        messages=[{
            "role": "user",
            "content": f"Analyze this data and identify the top 3 issues:\n\nMetrics: {state['metrics']}\n\nRaw data:\n{state['raw_data']}"
        }]
    )
    state["analysis"] = response.content[0].text
    print("Analysis complete.\n")
    return state

def generate_report(state: WorkflowState) -> WorkflowState:
    print("Step 4: Generating executive report...")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system="You are a chief of staff preparing a brief executive summary. No markdown, no bullets, no emojis. Plain text only. Keep it under 150 words.",
        messages=[{
            "role": "user",
            "content": f"Write a brief executive summary based on this analysis:\n\n{state['analysis']}"
        }]
    )
    state["report"] = response.content[0].text
    print("Report generated.\n")
    return state

# Build workflow
workflow = StateGraph(WorkflowState)

workflow.add_node("load_data", load_data)
workflow.add_node("calculate_metrics", calculate_metrics)
workflow.add_node("send_critical_alert", send_critical_alert)
workflow.add_node("analyze_data", analyze_data)
workflow.add_node("generate_report", generate_report)

workflow.set_entry_point("load_data")
workflow.add_edge("load_data", "calculate_metrics")

# Conditional routing after metrics
workflow.add_conditional_edges(
    "calculate_metrics",
    route_by_severity,
    {
        "critical": "send_critical_alert",
        "standard": "analyze_data"
    }
)

workflow.add_edge("send_critical_alert", "generate_report")
workflow.add_edge("analyze_data", "generate_report")
workflow.add_edge("generate_report", END)

app = workflow.compile()

print("=== Mainframe Operations Workflow ===\n")
result = app.invoke({
    "raw_data": "",
    "metrics": "",
    "success_rate": 0.0,
    "analysis": "",
    "report": "",
    "alert": ""
})

print("=== FINAL OUTPUT ===\n")
if result["alert"]:
    print("*** CRITICAL ALERT ***")
    print(result["alert"])
    print()
print("Executive Summary:")
print(result["report"])