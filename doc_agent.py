import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# Load the document
filepath = os.path.join(os.path.dirname(__file__), "sample_data.txt")
with open(filepath, "r") as f:
    document = f.read()

print("=== Document Q&A Agent ===")
print(f"Document loaded: sample_data.txt\n")

# Define tools
tools = [
    {
        "name": "search_document",
        "description": "Search the document for information related to a query",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for in the document"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "summarize_document",
        "description": "Get a full summary of the entire document",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Tool implementations
def search_document(query):
    lines = document.split('\n')
    relevant = [line for line in lines if any(word.lower() in line.lower() for word in query.split())]
    if relevant:
        return "\n".join(relevant)
    return "No relevant information found for that query."

def summarize_document():
    return document

def process_tool_call(tool_name, tool_input):
    if tool_name == "search_document":
        return search_document(tool_input["query"])
    elif tool_name == "summarize_document":
        return summarize_document()

# Agent loop
def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=f"You are a document analyst. You have access to a document and tools to search it. Answer questions accurately based only on what is in the document. No markdown, no bullets, no emojis. Plain text only.",
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
            final_response = next(block.text for block in response.content if hasattr(block, "text"))
            print(f"Agent: {final_response}\n")
            break

# Interactive loop
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    if not user_input.strip():
        continue
    run_agent(user_input)