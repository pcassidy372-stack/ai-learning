import os
import json
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()

client = anthropic.Anthropic()
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

TOPICS = [
    "IBM mainframe",
    "mainframe modernization",
    "COBOL modernization",
    "LinuxONE",
    "mainframe cloud migration",
    "Broadcom mainframe",
    "IBM z17",
    "mainframe data analytics",
    "fintech infrastructure",
    "mainframe talent shortage"
]

# Define tools
tools = [
    {
        "name": "search_news",
        "description": "Search for recent news articles on a specific topic",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to search for"
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "save_briefing",
        "description": "Save the final intelligence briefing to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The briefing content to save"
                }
            },
            "required": ["content"]
        }
    }
]

def search_news(topic):
    try:
        results = newsapi.get_everything(
            q=topic,
            language='en',
            sort_by='publishedAt',
            page_size=5
        )
        if results['totalResults'] == 0:
            return f"No recent articles found for: {topic}"
        
        articles = []
        for article in results['articles']:
            articles.append({
                "title": article['title'],
                "source": article['source']['name'],
                "published": article['publishedAt'][:10],
                "description": article['description']
            })
        return json.dumps(articles, indent=2)
    except Exception as e:
        return f"Search error: {str(e)}"

def save_briefing(content):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"intel_briefing_{timestamp}.txt"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "w") as f:
        f.write(f"MAINFRAME INDUSTRY INTELLIGENCE BRIEFING\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(content)
    return f"Briefing saved as {filename}"

def process_tool_call(tool_name, tool_input):
    if tool_name == "search_news":
        return search_news(tool_input["topic"])
    elif tool_name == "save_briefing":
        return save_briefing(tool_input["content"])

def run_agent():
    print("=== Mainframe Industry Intelligence Agent ===\n")
    print(f"Monitoring {len(TOPICS)} topics...\n")

    topics_str = "\n".join(f"- {t}" for t in TOPICS)
    
    messages = [{
        "role": "user",
        "content": f"""You are an intelligence analyst monitoring the mainframe industry for a Chief of Staff at a major fintech company.

Search for recent news on these topics:
{topics_str}

For each topic, search for articles and identify what is significant. Then write a concise intelligence briefing that covers:
1. The most important developments this week
2. Trends worth monitoring
3. Any threats or opportunities for enterprise mainframe operations

Keep it professional, concise, and actionable. Save the final briefing when done.
No markdown formatting. Plain text only."""
    }]

    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [Searching: {block.input.get('topic', 'saving briefing')}]")
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        else:
            final = next(block.text for block in response.content if hasattr(block, "text"))
            print("\n=== INTELLIGENCE BRIEFING ===\n")
            print(final)
            break

run_agent()