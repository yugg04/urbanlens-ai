from dotenv import load_dotenv
import os
import requests
import streamlit as st

load_dotenv()

from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from tavily import TavilyClient


# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UrbanLens — AI City Intelligence Agent",
    page_icon="🏙️",
    layout="wide",
)


# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "lc_messages" not in st.session_state:
    st.session_state.lc_messages = []

if "pending_tool_call" not in st.session_state:
    st.session_state.pending_tool_call = None

if "awaiting_approval" not in st.session_state:
    st.session_state.awaiting_approval = False

if "tool_results_queue" not in st.session_state:
    st.session_state.tool_results_queue = []


# ─────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """Get current weather of a city"""

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return "Missing OpenWeather API key"

    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city},IN&appid={api_key}&units=metric"
    )

    try:
        response = requests.get(url, timeout=8)
        data = response.json()

        if str(data.get("cod")) != "200":
            return f"Error: {data.get('message', 'Could not fetch weather')}"

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        feels_like = data["main"]["feels_like"]

        return (
            f"Weather in {city}: {desc}, {temp}°C "
            f"(feels like {feels_like}°C), humidity {humidity}%"
        )

    except Exception as e:
        return f"Error fetching weather: {str(e)}"


@tool
def get_news(city: str) -> str:
    """Get latest news about a city"""

    try:
        tavily_client = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )

        response = tavily_client.search(
            query=f"latest news in {city}",
            search_depth="basic",
            max_results=3
        )

        results = response.get("results", [])

        if not results:
            return f"No news found for {city}"

        news_list = []

        for r in results:
            title = r.get("title", "No title")
            url = r.get("url", "")
            snippet = r.get("content", "")

            news_list.append(
                f"• {title}\n🔗 {url}\n{snippet[:120]}..."
            )

        return f"Latest news in {city}:\n\n" + "\n\n".join(news_list)

    except Exception as e:
        return f"Error fetching news: {str(e)}"


TOOLS = [get_weather, get_news]

TOOL_MAP = {
    tool.name: tool for tool in TOOLS
}


# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────
@st.cache_resource
def get_llm():

    return ChatMistralAI(
        model="mistral-small-2506"
    ).bind_tools(TOOLS)


llm = get_llm()


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.title("🏙️ UrbanLens — AI City Intelligence Agent")

st.caption(
    "Weather · News · Human Approved Tool Calls"
)


# ─────────────────────────────────────────────
# Display Messages
# ─────────────────────────────────────────────
for msg in st.session_state.messages:

    if msg["role"] == "user":

        with st.chat_message("user"):
            st.markdown(msg["content"])

    else:

        with st.chat_message("assistant"):
            st.markdown(msg["content"])


# ─────────────────────────────────────────────
# Approval UI
# ─────────────────────────────────────────────
if (
    st.session_state.awaiting_approval
    and st.session_state.pending_tool_call
):

    tc = st.session_state.pending_tool_call

    st.warning(
        f"Tool wants to execute: {tc['name']}"
    )

    st.code(str(tc["args"]))

    col1, col2 = st.columns(2)

    # APPROVE
    with col1:

        if st.button("Approve"):

            tool_fn = TOOL_MAP.get(tc["name"])

            if tool_fn:

                try:
                    result = tool_fn.invoke(tc["args"])

                except Exception as e:
                    result = f"Tool error: {e}"

            else:
                result = "Unknown tool"

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ {result}"
            })

            st.session_state.lc_messages.append(
                ToolMessage(
                    content=result,
                    tool_call_id=tc["id"]
                )
            )

            st.session_state.pending_tool_call = None
            st.session_state.awaiting_approval = False

            st.session_state.tool_results_queue.append(
                "continue"
            )

            st.rerun()

    # DENY
    with col2:

        if st.button("Deny"):

            denied_message = "Tool call denied by user."

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"🚫 {denied_message}"
            })

            st.session_state.lc_messages.append(
                ToolMessage(
                    content=denied_message,
                    tool_call_id=tc["id"]
                )
            )

            st.session_state.pending_tool_call = None
            st.session_state.awaiting_approval = False

            st.session_state.tool_results_queue.append(
                "continue"
            )

            st.rerun()


# ─────────────────────────────────────────────
# Continue After Tool Result
# ─────────────────────────────────────────────
if (
    st.session_state.tool_results_queue
    and not st.session_state.awaiting_approval
):

    st.session_state.tool_results_queue.clear()

    with st.spinner("Thinking..."):

        response = llm.invoke(
            st.session_state.lc_messages
        )

        if response.tool_calls:

            tc = response.tool_calls[0]

            st.session_state.pending_tool_call = {
                "name": tc["name"],
                "args": tc["args"],
                "id": tc["id"]
            }

            st.session_state.awaiting_approval = True

        else:

            st.session_state.lc_messages.append(
                response
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": response.content
            })

    st.rerun()


# ─────────────────────────────────────────────
# Chat Input
# ─────────────────────────────────────────────
user_input = st.chat_input(
    "Ask about weather or news..."
)


if (
    user_input
    and not st.session_state.awaiting_approval
):

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    st.session_state.lc_messages.append(
        HumanMessage(content=user_input)
    )

    with st.spinner("Thinking..."):

        response = llm.invoke(
            st.session_state.lc_messages
        )

        if response.tool_calls:

            tc = response.tool_calls[0]

            st.session_state.pending_tool_call = {
                "name": tc["name"],
                "args": tc["args"],
                "id": tc["id"]
            }

            st.session_state.awaiting_approval = True

        else:

            st.session_state.lc_messages.append(
                response
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": response.content
            })

    st.rerun()
