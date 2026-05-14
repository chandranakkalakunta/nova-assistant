import os
import json
from datetime import datetime
from google import genai
from tools import (
    search_jobs, plan_holiday, analyze_stock,
    find_restaurants, find_hotels, get_fitness_plan
)

# ── Configuration ──────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# ── Nova's Personality ─────────────────────────────────────
today = datetime.now().strftime("%A, %B %d, %Y")
NOVA_SYSTEM_PROMPT = f"""You are Nova, a warm, intelligent and 
highly capable personal AI assistant for Chandra Nakkalakunta, 
a Principal Cloud & AI/ML Architect based in Hyderabad, India.

Today is {today}.

YOUR PERSONALITY:
- Warm, friendly and professional
- Proactive — anticipate what Chandra needs
- Concise but thorough
- Use emojis naturally to make responses engaging
- Address Chandra by name occasionally

YOUR KNOWLEDGE ABOUT CHANDRA:
- Principal Cloud & AI/ML Architect, 20+ years experience
- Based in Hyderabad, India
- Fitness level: Intermediate, works out 6 days/week
- Fitness goal: General fitness
- Workout schedule: Mon=Chest/Triceps, Tue=Back/Biceps,
  Wed=Legs/Glutes, Thu=Shoulders/Arms, Fri=Core/Cardio,
  Sat=Full Body/Flexibility, Sun=Rest
- Interested in stocks: NVDA, GOOG, MSFT
- Looking for Cloud/AI/ML Architect roles in Hyderabad
- Family man — considers family for holiday planning

YOUR 6 TOOLS:
1. search_jobs — find suitable jobs in Hyderabad
2. plan_holiday — plan family holidays and trips
3. analyze_stock — analyze stocks and market trends
4. find_restaurants — find best restaurants
5. find_hotels — find best hotels
6. get_fitness_plan — get daily personalized workout

DECISION RULES:
- Jobs, career, roles, hiring → search_jobs
- Holiday, travel, trip, vacation → plan_holiday
- Stock, share, invest, market, NVDA, GOOG → analyze_stock
- Restaurant, food, dining, eat → find_restaurants
- Hotel, stay, accommodation → find_hotels
- Gym, workout, exercise, fitness, today's plan → get_fitness_plan
- Greetings/general chat → respond warmly, no tools needed
- Multiple topics → use MULTIPLE tools!

RESPONSE STYLE:
- Always be helpful and actionable
- For fitness: be motivating and specific
- For stocks: always include disclaimer
- For jobs: relate to Chandra's profile
- For travel: consider family needs
"""

# ── Agent Planning ─────────────────────────────────────────
def plan_tools(question: str) -> dict:
    """Ask Gemini which tools to use"""
    planning_prompt = f"""
{NOVA_SYSTEM_PROMPT}

User message: "{question}"

Decide which tools to use. Respond ONLY with valid JSON:
{{
    "needs_tools": true/false,
    "tools": ["tool1", "tool2"],
    "queries": {{
        "search_jobs": "specific job search query",
        "plan_holiday": "specific holiday query",
        "analyze_stock": "specific stock query",
        "find_restaurants": "specific restaurant query",
        "find_hotels": "specific hotel query",
        "get_fitness_plan": "specific fitness query"
    }},
    "reasoning": "why these tools"
}}

Only include tools that are actually needed.
If just a greeting or general question, set needs_tools to false.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=planning_prompt
    )
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except:
        return {"needs_tools": False, "tools": [], "queries": {}, "reasoning": "fallback"}

# ── Execute Tools ──────────────────────────────────────────
def execute_tools(plan: dict) -> dict:
    """Execute the planned tools"""
    tool_map = {
        "search_jobs": search_jobs,
        "plan_holiday": plan_holiday,
        "analyze_stock": analyze_stock,
        "find_restaurants": find_restaurants,
        "find_hotels": find_hotels,
        "get_fitness_plan": get_fitness_plan
    }
    results = {}
    for tool in plan.get("tools", []):
        if tool in tool_map:
            query = plan.get("queries", {}).get(tool, "")
            results[tool] = tool_map[tool](query)
    return results

# ── Synthesize Answer ──────────────────────────────────────
def synthesize(question: str, tool_results: dict) -> str:
    """Generate Nova's final response"""
    if tool_results:
        context = "\n\n".join([
            f"{tool.upper()} RESULTS:\n{result}"
            for tool, result in tool_results.items()
        ])
        prompt = f"""
{NOVA_SYSTEM_PROMPT}

Chandra asked: "{question}"

Information gathered:
{context}

Now respond as Nova — warm, helpful, specific and actionable.
Format the response clearly with sections if needed.
"""
    else:
        prompt = f"""
{NOVA_SYSTEM_PROMPT}

Chandra said: "{question}"

Respond naturally as Nova. If it's a greeting,
welcome Chandra warmly and briefly explain what you can help with.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ── Main Nova Function ─────────────────────────────────────
def ask_nova(question: str) -> dict:
    """Main entry point — ask Nova anything"""
    print(f"\n🌟 Nova processing: {question}")

    # Step 1 — Plan
    plan = plan_tools(question)
    print(f"🧠 Plan: {plan.get('reasoning', '')}")
    print(f"🔧 Tools: {plan.get('tools', [])}")

    # Step 2 — Execute tools
    tool_results = {}
    if plan.get("needs_tools"):
        tool_results = execute_tools(plan)

    # Step 3 — Synthesize
    answer = synthesize(question, tool_results)

    return {
        "answer": answer,
        "tools_used": plan.get("tools", []),
        "reasoning": plan.get("reasoning", "")
    }

# ── Test ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("🌟 Testing Nova...\n")
    print("=" * 50)

    # Test greeting
    result = ask_nova("Hello Nova!")
    print(f"Nova: {result['answer']}")
    print(f"Tools used: {result['tools_used']}")
    print("\n" + "=" * 50)

    # Test fitness
    result = ask_nova("What's my workout for today?")
    print(f"Nova: {result['answer'][:500]}")
