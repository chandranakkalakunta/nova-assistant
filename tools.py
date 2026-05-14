import os
import requests
from datetime import datetime
from tavily import TavilyClient
import wikipediaapi

# ── Configuration ──────────────────────────────────────────
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
wiki = wikipediaapi.Wikipedia(language='en', user_agent='NovaAssistant/1.0')

# ── Fitness Calendar ───────────────────────────────────────
FITNESS_CALENDAR = {
    0: {"day": "Monday",    "focus": "Chest & Triceps",
        "exercises": [
            "Bench Press: 4 sets × 10 reps",
            "Incline Dumbbell Press: 3 sets × 12 reps",
            "Cable Flyes: 3 sets × 15 reps",
            "Tricep Pushdowns: 3 sets × 12 reps",
            "Overhead Tricep Extension: 3 sets × 12 reps",
            "Dips: 3 sets × 10 reps"
        ]},
    1: {"day": "Tuesday",   "focus": "Back & Biceps",
        "exercises": [
            "Deadlifts: 4 sets × 8 reps",
            "Pull-ups: 3 sets × 10 reps",
            "Barbell Rows: 3 sets × 10 reps",
            "Lat Pulldowns: 3 sets × 12 reps",
            "Barbell Curls: 3 sets × 12 reps",
            "Hammer Curls: 3 sets × 12 reps"
        ]},
    2: {"day": "Wednesday", "focus": "Legs & Glutes",
        "exercises": [
            "Squats: 4 sets × 10 reps",
            "Romanian Deadlifts: 3 sets × 12 reps",
            "Leg Press: 3 sets × 15 reps",
            "Lunges: 3 sets × 12 reps each leg",
            "Leg Curls: 3 sets × 12 reps",
            "Calf Raises: 4 sets × 20 reps"
        ]},
    3: {"day": "Thursday",  "focus": "Shoulders & Arms",
        "exercises": [
            "Overhead Press: 4 sets × 10 reps",
            "Lateral Raises: 3 sets × 15 reps",
            "Front Raises: 3 sets × 12 reps",
            "Face Pulls: 3 sets × 15 reps",
            "Preacher Curls: 3 sets × 12 reps",
            "Skull Crushers: 3 sets × 12 reps"
        ]},
    4: {"day": "Friday",    "focus": "Core & Cardio",
        "exercises": [
            "Plank: 3 sets × 60 seconds",
            "Crunches: 3 sets × 20 reps",
            "Russian Twists: 3 sets × 20 reps",
            "Leg Raises: 3 sets × 15 reps",
            "Mountain Climbers: 3 sets × 30 reps",
            "30 minutes moderate cardio (treadmill/cycling)"
        ]},
    5: {"day": "Saturday",  "focus": "Full Body & Flexibility",
        "exercises": [
            "Burpees: 3 sets × 15 reps",
            "Kettlebell Swings: 3 sets × 20 reps",
            "Box Jumps: 3 sets × 10 reps",
            "Push-ups: 3 sets × 20 reps",
            "Yoga/Stretching: 20 minutes",
            "Foam Rolling: 10 minutes"
        ]},
    6: {"day": "Sunday",    "focus": "Rest & Recovery",
        "exercises": [
            "Light walking: 30 minutes",
            "Gentle stretching: 15 minutes",
            "Meditation: 10 minutes",
            "Rest and recover — you earned it! 🧘"
        ]}
}

# ── Tool 1 — Job Search ────────────────────────────────────
def search_jobs(query: str) -> str:
    """Search for jobs in Hyderabad"""
    print(f"🔍 Searching jobs: {query}")
    try:
        results = tavily_client.search(
            query=f"{query} jobs Hyderabad India 2025",
            max_results=5,
            search_depth="advanced"
        )
        output = ["Latest job opportunities found:\n"]
        for r in results["results"]:
            output.append(f"• {r['title']}\n  {r['content'][:200]}\n  Source: {r['url']}\n")
        return "\n".join(output)
    except Exception as e:
        return f"Job search failed: {str(e)}"

# ── Tool 2 — Holiday Planner ───────────────────────────────
def plan_holiday(query: str) -> str:
    """Plan family holidays"""
    print(f"🌴 Planning holiday: {query}")
    try:
        results = tavily_client.search(
            query=f"{query} family holiday travel guide best time",
            max_results=5,
            search_depth="advanced"
        )
        output = ["Holiday planning information:\n"]
        for r in results["results"]:
            output.append(f"• {r['title']}\n  {r['content'][:200]}\n")

        # Also get Wikipedia info
        destination = query.split()[0]
        page = wiki.page(destination)
        if page.exists():
            output.append(f"\nAbout {destination}:\n{page.summary[:500]}")
        return "\n".join(output)
    except Exception as e:
        return f"Holiday planning failed: {str(e)}"

# ── Tool 3 — Stock Analyzer ───────────────────────────────
def analyze_stock(query: str) -> str:
    """Analyze stocks and market trends"""
    print(f"📈 Analyzing stock: {query}")
    try:
        results = tavily_client.search(
            query=f"{query} stock analysis news price forecast 2025",
            max_results=5,
            search_depth="advanced"
        )
        output = ["Stock analysis and market data:\n"]
        for r in results["results"]:
            output.append(f"• {r['title']}\n  {r['content'][:200]}\n")
        output.append("\n⚠️ Disclaimer: This is for informational purposes only. Not financial advice. Please consult a financial advisor before investing.")
        return "\n".join(output)
    except Exception as e:
        return f"Stock analysis failed: {str(e)}"

# ── Tool 4 — Restaurant Finder ────────────────────────────
def find_restaurants(query: str) -> str:
    """Find best restaurants"""
    print(f"🍽️ Finding restaurants: {query}")
    try:
        results = tavily_client.search(
            query=f"best {query} restaurants Hyderabad highly rated 2025",
            max_results=5,
            search_depth="advanced"
        )
        output = ["Restaurant recommendations:\n"]
        for r in results["results"]:
            output.append(f"• {r['title']}\n  {r['content'][:200]}\n")
        return "\n".join(output)
    except Exception as e:
        return f"Restaurant search failed: {str(e)}"

# ── Tool 5 — Hotel Finder ─────────────────────────────────
def find_hotels(query: str) -> str:
    """Find best hotels"""
    print(f"🏨 Finding hotels: {query}")
    try:
        results = tavily_client.search(
            query=f"best {query} hotels highly rated amenities price",
            max_results=5,
            search_depth="advanced"
        )
        output = ["Hotel recommendations:\n"]
        for r in results["results"]:
            output.append(f"• {r['title']}\n  {r['content'][:200]}\n")
        return "\n".join(output)
    except Exception as e:
        return f"Hotel search failed: {str(e)}"

# ── Tool 6 — Fitness Advisor ──────────────────────────────
def get_fitness_plan(query: str) -> str:
    """Get personalized daily fitness plan"""
    print(f"💪 Getting fitness plan: {query}")

    # Get today's day
    today = datetime.now().weekday()  # 0=Monday, 6=Sunday
    today_plan = FITNESS_CALENDAR[today]

    # Check for modifications in query
    query_lower = query.lower()

    # Handle special requests
    if "tomorrow" in query_lower:
        tomorrow = (today + 1) % 7
        plan = FITNESS_CALENDAR[tomorrow]
        header = f"Tomorrow's workout ({plan['day']}):"
    elif "rest" in query_lower or "skip" in query_lower:
        return """💆 Taking a rest day is smart training!
        
Here's what to do on a rest day:
- Light walking: 20-30 minutes
- Gentle stretching: 15 minutes  
- Stay hydrated
- Get 7-8 hours sleep
- Eat protein-rich meals for recovery

Remember: Muscles grow during REST, not during workouts! 💪"""
    elif "light" in query_lower or "easy" in query_lower:
        plan = today_plan
        header = f"Light version — {plan['day']} ({plan['focus']}):"
        exercises = [ex.replace("4 sets", "2 sets").replace("3 sets", "2 sets") for ex in plan['exercises']]
        result = f"💪 {header}\n\n"
        result += f"Focus: {plan['focus']} (Light intensity)\n\n"
        for ex in exercises:
            result += f"✓ {ex}\n"
        result += "\n💡 Tip: Light days are still valuable — maintain form, reduce weight by 40%"
        return result
    else:
        plan = today_plan
        header = f"Today's workout ({plan['day']}):"

    # Build response
    result = f"💪 {header}\n\n"
    result += f"🎯 Focus: {plan['focus']}\n\n"
    result += "📋 Your exercises:\n"
    for ex in plan['exercises']:
        result += f"  ✓ {ex}\n"
    result += f"\n⏱️ Estimated time: 60-75 minutes"
    result += f"\n💡 Tip: Warm up 5-10 minutes before starting"
    result += f"\n🥤 Stay hydrated — drink water between sets!"
    return result

# ── Test ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing Nova tools...\n")
    print("=" * 50)

    # Test fitness (no API needed)
    print(get_fitness_plan("what should I do today"))
    print("\n" + "=" * 50)

    # Test job search
    result = search_jobs("Cloud Architect AI")
    print(result[:300])
