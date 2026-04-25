import os
import json
import anthropic
import streamlit as st
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

tools = [
    {
        "name": "search_news",
        "description": "Search for recent news articles on a specific topic",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The topic to search for"}
            },
            "required": ["topic"]
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

def process_tool_call(tool_name, tool_input):
    if tool_name == "search_news":
        return search_news(tool_input["topic"])

def run_agent():
    topics_str = "\n".join(f"- {t}" for t in TOPICS)
    messages = [{
        "role": "user",
        "content": f"""You are an intelligence analyst for a Chief of Staff at a major fintech company.

Search for recent news on these topics:
{topics_str}

Then return a structured briefing in this exact format:

EXECUTIVE SUMMARY
[Write exactly 5 concise bullet points starting with - that capture the most important developments]

KEY DEVELOPMENTS
[Write 3-4 paragraphs covering the most significant findings in detail]

TRENDS TO WATCH
[Write 2-3 paragraphs on emerging patterns worth monitoring]

RECOMMENDED ACTIONS
[Write 3-5 specific actions for a fintech Chief of Staff]

No markdown formatting. No bold text. No asterisks. Plain text only."""
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

def parse_briefing(text):
    sections = {
        "executive_summary": "",
        "key_developments": "",
        "trends": "",
        "actions": ""
    }
    
    current = None
    lines = text.split('\n')
    buffer = []
    
    for line in lines:
        if "EXECUTIVE SUMMARY" in line.upper():
            current = "executive_summary"
            buffer = []
        elif "KEY DEVELOPMENTS" in line.upper():
            sections["executive_summary"] = '\n'.join(buffer).strip()
            current = "key_developments"
            buffer = []
        elif "TRENDS TO WATCH" in line.upper():
            sections["key_developments"] = '\n'.join(buffer).strip()
            current = "trends"
            buffer = []
        elif "RECOMMENDED ACTIONS" in line.upper():
            sections["trends"] = '\n'.join(buffer).strip()
            current = "actions"
            buffer = []
        elif current:
            buffer.append(line)
    
    if current == "actions":
        sections["actions"] = '\n'.join(buffer).strip()
    
    return sections

# --- Streamlit UI ---
st.set_page_config(
    page_title="Mainframe Intelligence Briefing",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Mainframe Industry Intelligence")
st.caption(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
st.divider()

if 'briefing' not in st.session_state:
    with st.spinner("Gathering intelligence across 10 topics..."):
        st.session_state.briefing = run_agent()
        st.session_state.generated_at = datetime.now().strftime('%B %d, %Y %I:%M %p')

sections = parse_briefing(st.session_state.briefing)

# Executive Summary
st.subheader("Executive Summary")
if sections["executive_summary"]:
    for line in sections["executive_summary"].split('\n'):
        if line.strip().startswith('-'):
            st.markdown(f"**{line.strip()[1:].strip()}**")
        elif line.strip():
            st.write(line.strip())
else:
    st.write(st.session_state.briefing[:500])

st.divider()

# Detail sections in columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Key Developments")
    st.write(sections["key_developments"] or "See full briefing below.")

with col2:
    st.subheader("Trends to Watch")
    st.write(sections["trends"] or "See full briefing below.")

st.divider()

# Refresh button
if st.button("Refresh Briefing"):
    del st.session_state['briefing']
    st.rerun()

# Full briefing expander
with st.expander("View Full Raw Briefing"):
    st.text(st.session_state.briefing)