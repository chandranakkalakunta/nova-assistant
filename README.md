# 🌟 Nova — Personal AI Assistant

> *"Your intelligent personal assistant — always here to help!"*

Nova is a personalized AI assistant built on Google Cloud Platform, powered by Google Gemini 2.5 Flash. Nova knows who you are, understands your schedule, and helps you with jobs, travel, fitness, stocks, and more — all in one place.

🌐 **Live Demo:** [https://nova-assistant-716553701658.us-central1.run.app](https://nova-assistant-716553701658.us-central1.run.app)

---

## 🎯 What Nova Can Do

| Tool | What Nova Does | Example |
|------|----------------|---------|
| 🔍 Job Search | Find suitable roles in Hyderabad | "Find Cloud Architect jobs" |
| 🌴 Holiday Planner | Plan family holidays & itineraries | "Plan a 5-day Goa trip" |
| 📈 Stock Analyzer | Analyze stocks & market trends | "Analyze NVDA stock" |
| 🍽️ Restaurant Finder | Find best restaurants near you | "Best biryani in Hyderabad" |
| 🏨 Hotel Finder | Find best hotels for trips | "Hotels in Goa under ₹5000" |
| 💪 Fitness Advisor | Personalized daily workout plan | "What's my workout today?" |

---

## 🧠 What Makes Nova Special

Unlike generic AI assistants, Nova is **deeply personalized:**

```
Nova knows:
✅ Your name and location (Hyderabad)
✅ Your fitness schedule (6-day split)
✅ Your workout focus for each day
✅ Your stock interests (NVDA, GOOG, MSFT)
✅ Your career goals (Cloud/AI/ML Architect)
✅ Your family travel preferences
```

---

## 💪 Personalized Fitness Calendar

Nova knows your exact workout schedule:

| Day | Focus |
|-----|-------|
| Monday | Chest & Triceps |
| Tuesday | Back & Biceps |
| Wednesday | Legs & Glutes |
| Thursday | Shoulders & Arms |
| Friday | Core & Cardio |
| Saturday | Full Body & Flexibility |
| Sunday | Rest & Recovery 🧘 |

Ask Nova: *"What's my workout today?"* and she gives you the exact exercises, sets, and reps — no setup needed!

---

## 🏗️ Architecture

```
User Question
      │
      ▼
┌─────────────────────────────────┐
│   Nova Agent (Gemini 2.5 Flash) │
│                                 │
│   Step 1: Understand request    │
│   Step 2: Decide which tools    │
│   Step 3: Execute tools         │
│   Step 4: Personalized response │
└──────┬──────────────────────────┘
       │
       ├──► 🔍 Job Search (Tavily)
       ├──► 🌴 Holiday Planner (Tavily + Wikipedia)
       ├──► 📈 Stock Analyzer (Tavily)
       ├──► 🍽️ Restaurant Finder (Tavily)
       ├──► 🏨 Hotel Finder (Tavily)
       └──► 💪 Fitness Advisor (Built-in Calendar)
                 │
                 ▼
        Personalized Answer ✅
```

---

## 📊 Observability

Nova has production-grade structured observability built in via `observability.py`.
Every request is fully instrumented across 3 layers:

```
Layer 1 — Request logging
  → request_start: question preview, session_id
  → request_end:   latency_ms, tools_used, success/failure

Layer 2 — Tool execution logging
  → tool_start:   tool_name, query
  → tool_success: tool_name, latency_ms, result_size
  → tool_error:   tool_name, error_type, error_message

Layer 3 — Gemini call logging
  → gemini_call_success: call_type, latency_ms, input_tokens,
                         output_tokens, total_tokens
  → gemini_call_error:   call_type, latency_ms, error_type
```

Logs are structured JSON ingested automatically by **Google Cloud Logging**.

### Querying logs in Cloud Logging

```
# All Nova logs
resource.type="cloud_run_revision"

# Slow tool executions
resource.type="cloud_run_revision"
jsonPayload.event="tool_success"
jsonPayload.latency_ms > 3000

# All errors
resource.type="cloud_run_revision"
jsonPayload.event="tool_error"

# Trace a specific request end-to-end
resource.type="cloud_run_revision"
jsonPayload.request_id="req_1234567890"

# Gemini token usage
resource.type="cloud_run_revision"
jsonPayload.event="gemini_call_success"
```

---


## 🔐 Security Architecture

Nova implements production-grade security:

### Secret Management
API keys stored in **Google Cloud Secret Manager** — never in environment variables or code:

```bash
# Secrets stored securely
gcloud secrets list --project=nova-assistant-chandra
# gemini-api-key  → Gemini API key (encrypted at rest)
# tavily-api-key  → Tavily API key (encrypted at rest)
```

### Service Account (Least Privilege)
Nova runs as dedicated `nova-sa` service account with minimum required permissions:

| Permission | Purpose |
|------------|---------|
| `secretmanager.secretAccessor` | Read API keys from Secret Manager |
| `aiplatform.user` | Call Gemini API |
| `logging.logWriter` | Write structured logs |

No other permissions granted — principle of least privilege! ✅

### Security Best Practices
- ✅ No hardcoded credentials anywhere in code
- ✅ API keys encrypted at rest in Secret Manager
- ✅ Dedicated service account per application
- ✅ Audit trail of all secret access
- ✅ Keys rotatable without redeployment
- ✅ Docker build optimized (.dockerignore — 93% faster!)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM & Agent Brain | Google Gemini 2.5 Flash |
| Web Search | Tavily Search API |
| Encyclopedia | Wikipedia API |
| Web UI | Streamlit |
| Containerization | Docker |
| Cloud Deployment | Google Cloud Run |
| Image Registry | Google Artifact Registry |
| Observability | Google Cloud Logging (structured JSON) |
| Secret Management | Google Cloud Secret Manager |
| Identity & Access | Google Cloud IAM + Service Accounts |

---

## ☁️ GCP Project Details

| Resource | Value |
|----------|-------|
| Project ID | `nova-assistant-chandra` |
| Project Number | `716553701658` |
| Region | `us-central1` |
| Artifact Registry | `nova-repo` |
| Cloud Run Service | `nova-assistant` |
| Live URL | `https://nova-assistant-716553701658.us-central1.run.app` |

---

## 💡 Key Design — Personal Context Injection

Nova's secret is **personal context baked into every response:**

```python
NOVA_SYSTEM_PROMPT = """
You are Nova, personal assistant for Chandra Nakkalakunta.
Today is {today}.

YOUR KNOWLEDGE ABOUT CHANDRA:
- Principal Cloud & AI/ML Architect, Hyderabad
- Fitness: Intermediate, 6 days/week
- Stocks: NVDA, GOOG, MSFT
- Looking for: Cloud/AI/ML roles in Hyderabad
...
"""
```

Every response is tailored — Nova never forgets who she's talking to!

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- Tavily API key from [Tavily](https://tavily.com)
- Google Cloud SDK (`gcloud`) installed and authenticated

### Local Setup

```bash
# Clone the repository
git clone https://github.com/chandranakkalakunta/nova-assistant.git
cd nova-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API keys
export GEMINI_API_KEY="your-gemini-key"
export TAVILY_API_KEY="your-tavily-key"

# Run Nova
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🐳 Docker Deployment

```bash
# Set your API keys first
export GEMINI_API_KEY="your-gemini-key"
export TAVILY_API_KEY="your-tavily-key"

# Build for AMD64 (Cloud Run requirement)
docker buildx build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/nova-assistant-chandra/nova-repo/nova-assistant:latest \
  --push .

# Deploy to Cloud Run with Secret Manager
gcloud run deploy nova-assistant \
  --image us-central1-docker.pkg.dev/nova-assistant-chandra/nova-repo/nova-assistant:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account=nova-sa@nova-assistant-chandra.iam.gserviceaccount.com \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest \
  --memory 2Gi \
  --port 8080
```

> ⚠️ Always verify `echo $GEMINI_API_KEY` and `echo $TAVILY_API_KEY` are non-empty
> before deploying. Empty env vars are a common deployment pitfall.

---

## 📁 Project Structure

```
nova-assistant/
├── app.py              # Streamlit web UI with chat interface
├── nova.py             # Nova's brain — agent logic & personality
├── tools.py            # 6 specialized tools
├── observability.py    # Structured logging for Cloud Logging
├── Dockerfile          # Container configuration
├── .dockerignore       # Docker build exclusions
├── requirements.txt    # Python dependencies
├── .dockerignore       # Docker build exclusions (93% faster builds!)
├── .gitignore          # Git exclusions
└── README.md           # This file
```

---

## 🗺️ Roadmap

### Phase 2 — Security & Observability (Completed ✅)
- [x] ✅ Structured JSON logging — Cloud Logging
- [x] ✅ Per-request UUID tracking
- [x] ✅ Per-tool execution logging with timing
- [x] ✅ Gemini token usage tracking (cost monitoring)
- [x] ✅ Health check endpoint (port 8081)
- [x] ✅ Uptime monitoring (global, 5-min intervals)
- [x] ✅ Alert policy (email notification on downtime)
- [x] ✅ Secret Manager (encrypted API key storage)
- [x] ✅ Dedicated Service Account (least privilege)
- [x] ✅ Docker optimization (.dockerignore — 212s → 15s builds!)
- [ ] 📊 Cloud Monitoring dashboard
- [ ] 🔔 Error rate alerting

### Phase 3 — Advanced Features (Coming Soon)
- [ ] 🎙️ Voice interface — speak to Nova, Nova speaks back
- [ ] 📱 PWA — installable on Android home screen
- [ ] 🧠 Memory across sessions
- [ ] 📅 Proactive daily briefings
- [ ] 🏨 Hotel & restaurant booking integration

### Phase 4 — Future
- [ ] Native Android app
- [ ] iOS support
- [ ] Calendar integration
- [ ] WhatsApp integration
- [ ] More personalization

---

## 👨‍💻 Author

**Chandra Nakkalakunta**
Principal Cloud & AI/ML Architect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/chandra-nakkalakunta)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/chandranakkalakunta)

---

## 🔗 Related Projects

- [Smart Document Q&A Bot](https://github.com/chandranakkalakunta/doc-qa-bot) — RAG-based document Q&A
- [AI Resume Analyzer](https://github.com/chandranakkalakunta/resume-analyzer) — AI-powered resume matching
- [AI Job Search Agent](https://github.com/chandranakkalakunta/job-search-agent) — Multi-source job intelligence

---

## 📄 License

MIT License — feel free to use this project as a reference.
