import streamlit as st
import os
from datetime import datetime
from nova import ask_nova

# ── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Nova — Personal AI Assistant",
    page_icon="🌟",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .nova-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    .nova-title {
        color: #e2c97e;
        font-size: 42px;
        font-weight: bold;
        margin: 0;
    }
    .nova-subtitle {
        color: #a8b2d8;
        font-size: 16px;
        margin-top: 5px;
    }
    .tool-badge {
        display: inline-block;
        background: #0f3460;
        color: #e2c97e;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
    }
    .suggestion-btn {
        background: #1a1a2e;
        border: 1px solid #e2c97e;
        color: #e2c97e;
        padding: 5px 10px;
        border-radius: 8px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────
st.markdown("""
<div class="nova-header">
    <p class="nova-title">🌟 Nova</p>
    <p class="nova-subtitle">Your Personal AI Assistant — Always here to help, Chandra!</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌟 Nova's Capabilities")
    st.markdown("""
    | Tool | What Nova does |
    |------|----------------|
    | 🔍 | Find jobs in Hyderabad |
    | 🌴 | Plan family holidays |
    | 📈 | Analyze stocks |
    | 🍽️ | Find restaurants |
    | 🏨 | Find hotels |
    | 💪 | Daily workout plan |
    """)

    st.divider()

    # Today's info
    now = datetime.now()
    st.markdown(f"### 📅 Today")
    st.markdown(f"**{now.strftime('%A, %B %d')}**")

    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    focus = ["Chest & Triceps","Back & Biceps","Legs & Glutes",
             "Shoulders & Arms","Core & Cardio","Full Body","Rest & Recovery"]
    today_idx = now.weekday()
    st.markdown(f"💪 **{focus[today_idx]}** day!")

    st.divider()

    # Quick actions
    st.markdown("### ⚡ Quick Ask")
    quick_questions = [
        "What's my workout today?",
        "Find Cloud Architect jobs",
        "Analyze NVDA stock",
        "Best restaurants in Hyderabad",
        "Plan a Goa family trip",
        "Find hotels in Goa"
    ]

    for q in quick_questions:
        if st.button(q, use_container_width=True):
            st.session_state.quick_question = q

    st.divider()
    st.caption("Built with ❤️ using Google Gemini + Tavily")
    st.caption("Nova v1.0 — Phase 1")

# ── Main Chat ──────────────────────────────────────────────

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"🌟 Hello Chandra! I'm Nova, your personal AI assistant!\n\nToday is **{datetime.now().strftime('%A, %B %d, %Y')}** and it's your **{focus[today_idx]}** day! 💪\n\nHow can I help you today? You can ask me about jobs, holidays, stocks, restaurants, hotels, or your workout!",
        "tools": []
    })

# Handle quick questions from sidebar
if "quick_question" in st.session_state:
    st.session_state.pending_question = st.session_state.quick_question
    del st.session_state.quick_question

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="🌟"):
            st.markdown(message["content"])
            if message.get("tools"):
                tool_icons = {
                    "search_jobs": "🔍 Jobs",
                    "plan_holiday": "🌴 Holiday",
                    "analyze_stock": "📈 Stocks",
                    "find_restaurants": "🍽️ Restaurants",
                    "find_hotels": "🏨 Hotels",
                    "get_fitness_plan": "💪 Fitness"
                }
                tools_html = " ".join([
                    f'<span class="tool-badge">{tool_icons.get(t, t)}</span>'
                    for t in message["tools"]
                ])
                st.markdown(f"*Used: {tools_html}*", unsafe_allow_html=True)

# ── Chat Input ─────────────────────────────────────────────
# Handle pending question from sidebar buttons
default_input = ""
if "pending_question" in st.session_state:
    default_input = st.session_state.pending_question
    del st.session_state.pending_question

question = st.chat_input("Ask Nova anything...", )

# Process question
if question or default_input:
    user_input = question or default_input

    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Get Nova's response
    with st.chat_message("assistant", avatar="🌟"):
        with st.spinner("🌟 Nova is thinking..."):
            result = ask_nova(user_input)

        st.markdown(result["answer"])

        # Show tools used
        if result["tools_used"]:
            tool_icons = {
                "search_jobs": "🔍 Jobs",
                "plan_holiday": "🌴 Holiday",
                "analyze_stock": "📈 Stocks",
                "find_restaurants": "🍽️ Restaurants",
                "find_hotels": "🏨 Hotels",
                "get_fitness_plan": "💪 Fitness"
            }
            tools_html = " ".join([
                f'<span class="tool-badge">{tool_icons.get(t, t)}</span>'
                for t in result["tools_used"]
            ])
            st.markdown(f"*Used: {tools_html}*", unsafe_allow_html=True)

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "tools": result["tools_used"]
    })
