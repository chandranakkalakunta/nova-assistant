import os
import json
from datetime import datetime
from google import genai
from tools import (
    search_jobs, plan_holiday, analyze_stock,
    find_restaurants, find_hotels, get_fitness_plan
)

# ── Observability ──────────────────────────────────────────
from observability import (
    get_secret,
    log_startup,
    log_request_start,
    log_request_end,
    log_tool_execution,
    log_gemini_call,
    log_error,
)

# ── Configuration ──────────────────────────────────────────
GEMINI_API_KEY = get_secret("gemini-api-key")
client = genai.Client(api_key=GEMINI_API_KEY)

# Log startup so we can verify deployments in Cloud Logging
log_startup()

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
def plan_tools(question: str, request_id: str) -> dict:
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

    with log_gemini_call("planning", request_id) as ctx:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=planning_prompt
        )
        # Capture token usage if available
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            ctx["input_tokens"] = getattr(response.usage_metadata, "prompt_token_count", 0)
            ctx["output_tokens"] = getattr(response.usage_metadata, "candidates_token_count", 0)
            ctx["total_tokens"] = getattr(response.usage_metadata, "total_token_count", 0)

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except:
        return {"needs_tools": False, "tools": [], "queries": {}, "reasoning": "fallback"}


# ── Execute Tools ──────────────────────────────────────────
def execute_tools(plan: dict, request_id: str) -> dict:
    """Execute the planned tools with per-tool observability"""
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

            try:
                with log_tool_execution(tool, query, request_id) as ctx:
                    result = tool_map[tool](query)
                    ctx["result_size"] = len(str(result))
                    results[tool] = result

            except Exception as e:
                # Log already happened inside context manager
                # Return graceful degradation — don't fail entire request
                results[tool] = f"[Tool unavailable: {type(e).__name__}]"

    return results


# ── Synthesize Answer ──────────────────────────────────────
def synthesize(question: str, tool_results: dict, request_id: str) -> str:
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

    with log_gemini_call("synthesis", request_id) as ctx:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            ctx["input_tokens"] = getattr(response.usage_metadata, "prompt_token_count", 0)
            ctx["output_tokens"] = getattr(response.usage_metadata, "candidates_token_count", 0)
            ctx["total_tokens"] = getattr(response.usage_metadata, "total_token_count", 0)

    return response.text


# ── Main Nova Function ─────────────────────────────────────
def ask_nova(question: str, session_id: str = None) -> dict:
    """Main entry point — ask Nova anything"""

    # Start request tracking
    req_ctx = log_request_start(question, session_id)
    request_id = req_ctx["request_id"]

    try:
        # Step 1 — Plan (with Gemini call logging)
        plan = plan_tools(question, request_id)

        # Step 2 — Execute tools (with per-tool logging)
        tool_results = {}
        if plan.get("needs_tools"):
            tool_results = execute_tools(plan, request_id)

        # Step 3 — Synthesize (with Gemini call logging)
        answer = synthesize(question, tool_results, request_id)

        # Log successful request completion
        log_request_end(req_ctx, plan.get("tools", []), success=True)

        return {
            "answer": answer,
            "tools_used": plan.get("tools", []),
            "reasoning": plan.get("reasoning", ""),
            "request_id": request_id,  # Return for UI correlation
        }

    except Exception as e:
        log_error("Nova request failed unexpectedly", e, request_id)
        log_request_end(req_ctx, [], success=False)
        raise


# ── Test ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("🌟 Testing Nova with observability...\n")
    print("=" * 50)

    result = ask_nova("Hello Nova!")
    print(f"Nova: {result['answer']}")
    print(f"Tools used: {result['tools_used']}")
    print(f"Request ID: {result['request_id']}")

    print("\n" + "=" * 50)

    result = ask_nova("What's my workout for today?")
    print(f"Nova: {result['answer'][:500]}")
    print(f"Request ID: {result['request_id']}")
# test
