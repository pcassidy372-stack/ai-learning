import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform a math calculation",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }
]

def get_weather(city):
    weather_data = {
        "new york": "72°F, partly cloudy",
        "london": "58°F, rainy",
        "tokyo": "68°F, sunny",
        "westfield": "65°F, clear skies"
    }
    return weather_data.get(city.lower(), "Weather data unavailable for that city")

def calculate(expression):
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except:
        return "Could not calculate that expression"

def process_tool_call(tool_name, tool_input):
    if tool_name == "get_weather":
        return get_weather(tool_input["city"])
    elif tool_name == "calculate":
        return calculate(tool_input["expression"])

def run_agent(user_message):
    print(f"You: {user_message}\n")
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "tool_use":
            # Handle ALL tool calls in this response
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"Agent using tool: {block.name}")
                    print(f"With input: {block.input}\n")
                    
                    result = process_tool_call(block.name, block.input)
                    print(f"Tool result: {result}\n")
                    
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

run_agent("What's the weather in Westfield and what is 847 * 23?")