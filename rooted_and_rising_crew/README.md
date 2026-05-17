# 🌱 Rooted and Rising

> *Grounded in values. Growing every day.*

A multi-agent AI system built with **CrewAI** that helps Indian parents track, plan, and celebrate their child's holistic growth — across academics, health, values, creativity, and family bonds.

---

## What it does

| Job | What happens |
|-----|-------------|
| **Journal** | Log what your child did today — text, photos, voice notes |
| **Analyse** | Detect which of the 5 growth domains are being neglected |
| **Plan** | Get AI suggestions + add your own planned activities |
| **Nudge** | Receive smart alerts when a domain goes quiet too long |
| **Library** | Auto-build a living record of books read, foods loved, skills mastered |
| **Report** | Generate a beautiful PDF at month-end — achievements, photos, growth notes |

---

## The 5 growth domains

```
1. Academics & Reading       → homework, books, curiosity
2. Outdoor & Health          → biking, sports, nutrition, sleep
3. Values & Religious Ed     → character, empathy, spiritual grounding
4. Family & Friends          → bonding time, social skills, screen balance
5. Creative Pursuits         → art, music, dance, imagination
```

---

## Architecture

```
                        ┌─────────────────────┐
                        │   Orchestrator       │
                        │   (CrewAI Manager)   │
                        └─────────┬───────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
   ┌──────┴────────┐    ┌─────────┴─────────┐   ┌────────┴────────┐
   │   Journal     │    │ Balance Analyser   │   │    Planner      │
   │   Agent       │    │    Agent           │   │    Agent        │
   └──────┬────────┘    └─────────┬─────────┘   └────────┬────────┘
          │                       │                       │
   ┌──────┴────────┐    ┌─────────┴─────────┐   ┌────────┴────────┐
   │   Library     │    │    Nudge           │   │    Report       │
   │   Agent       │    │    Agent           │   │    Agent        │
   └───────────────┘    └───────────────────┘   └─────────────────┘
```

### Agents

| Agent | Responsibility |
|-------|---------------|
| `JournalAgent` | Classifies free-text/image/audio input into structured `JournalEntry` |
| `BalanceAnalyserAgent` | Detects domain gaps over rolling 7/30-day windows, produces `GapReport` |
| `PlannerAgent` | Generates AI activity suggestions + accepts parent-defined todos |
| `LibraryAgent` | Auto-populates Books / Foods / Activities collections from journal entries |
| `NudgeAgent` | Fires throttled in-app alerts when domains fall behind |
| `ReportAgent` | Generates a monthly PDF with photos, stats, and highlights |

---

## Engineering concepts demonstrated

- **Agent specialisation** — single responsibility per agent, clean handoff contracts
- **Structured outputs** — every agent communicates via typed Pydantic v2 models
- **Human-in-the-loop** — parent approval gate before weekly plan is finalised
- **Fault tolerance** — domain crew failure = graceful partial output, never a crash
- **Observability** — structured JSON logs per agent run via `structlog`
- **Retry handling** — exponential backoff on LLM and external API calls
- **Free-tier first** — zero paid infrastructure; runs entirely on your laptop

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Agent framework | [CrewAI](https://crewai.com) | Multi-agent orchestration |
| LLM | `claude-3-5-haiku` via Anthropic API (free tier) | Fast, cheap, accurate |
| Backend API | FastAPI | Async, typed, auto-documented |
| Database | SQLite + SQLModel | Zero infra, local, production-quality ORM |
| PDF generation | WeasyPrint | HTML/CSS → PDF, free, beautiful |
| Frontend | React + Vite + Chart.js | Fast dev server, zero cost |
| Logging | structlog | Structured, queryable logs |
| Config | pydantic-settings | Type-safe env config |
| Testing | pytest + pytest-asyncio | Async-first test suite |
| Package management | uv | Fast, modern Python packaging |
| Version control | GitHub | Source of truth |

---

## Free tools used

| Tool | Purpose | Cost |
|------|---------|------|
| Anthropic API | LLM calls (haiku model) | Free tier available |
| OpenWeatherMap API | Weather checks for outdoor planning | Free tier (1000 calls/day) |
| Open Library API | Book metadata lookup | Completely free |
| Notion API | Optional: mirror journal to Notion | Free tier |
| GitHub | Version control + project board | Free |
| SQLite | Local database | Free, built into Python |

---

## Project structure

```
rooted-and-rising/
├── README.md
├── PRD.md
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── config.py                # pydantic-settings config
│   ├── database.py              # SQLite + SQLModel setup
│   │
│   ├── models/                  # Pydantic v2 data contracts
│   │   ├── journal.py           # JournalEntry, MediaAttachment
│   │   ├── analysis.py          # GapReport, DomainScore
│   │   ├── planning.py          # WeeklyPlan, PlannedActivity
│   │   ├── library.py           # BookItem, FoodItem, ActivityItem
│   │   ├── nudge.py             # NudgeMessage
│   │   └── report.py            # MonthlyReport
│   │
│   ├── agents/                  # CrewAI agent definitions
│   │   ├── base.py              # BaseAgent with retry + logging
│   │   ├── journal_agent.py
│   │   ├── balance_analyser.py
│   │   ├── planner_agent.py
│   │   ├── library_agent.py
│   │   ├── nudge_agent.py
│   │   └── report_agent.py
│   │
│   ├── crews/                   # CrewAI crew definitions
│   │   └── orchestrator.py      # Master crew, approval gate
│   │
│   ├── tools/                   # External tool wrappers
│   │   ├── weather_tool.py
│   │   ├── books_tool.py
│   │   └── file_store.py
│   │
│   ├── api/                     # FastAPI route handlers
│   │   ├── journal.py
│   │   ├── library.py
│   │   ├── planning.py
│   │   └── reports.py
│   │
│   └── core/
│       ├── logging.py           # structlog setup
│       └── exceptions.py        # Domain exceptions
│
├── src/rooted_and_rising_crew/  # CrewAI crew package
│   ├── config/
│   │   ├── agents.yaml          # Agent definitions
│   │   └── tasks.yaml           # Task definitions
│   ├── crew.py                  # Crew wiring + logic
│   └── main.py                  # Entry point (crewai run)
│
├── frontend/                    # React + Vite app
│   └── src/
│       ├── pages/
│       ├── components/
│       └── api/
│
├── tests/
│   ├── unit/
│   │   ├── test_journal_agent.py
│   │   ├── test_balance_analyser.py
│   │   └── test_library_agent.py
│   └── integration/
│       └── test_full_flow.py
│
├── reports/                     # Generated PDFs land here
├── media/                       # Uploaded images/audio
└── docs/
    ├── architecture.md
    └── engineering-decisions.md
```

---

## Getting started

### Prerequisites
- Python 3.12+
- Node.js 20+
- `uv` (Python package manager)

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/rooted-and-rising.git
cd rooted-and-rising

# Install uv if you haven't already
pip install uv

# Install Python dependencies
uv sync

# Copy and fill in environment variables
cp .env.example .env
# Add your ANTHROPIC_API_KEY (and optionally OPENAI_API_KEY) to .env

# Initialise the database
uv run python -m backend.database

# Start the backend
uv run uvicorn backend.main:app --reload

# In a separate terminal, start the frontend
cd frontend && npm install && npm run dev
```

### Running the crew directly

```bash
# Run the CrewAI crew
crewai run

# Or via the project script
uv run rooted_and_rising_crew
```

### Customising agents and tasks

- Modify `src/rooted_and_rising_crew/config/agents.yaml` to define your agents
- Modify `src/rooted_and_rising_crew/config/tasks.yaml` to define your tasks
- Modify `src/rooted_and_rising_crew/crew.py` to add your own logic, tools and specific args
- Modify `src/rooted_and_rising_crew/main.py` to add custom inputs for your agents and tasks

---

## Build phases

- [x] Phase 1 — Scaffold: project structure, data models, DB, config, logging
- [ ] Phase 2 — Journal agent: text + image + audio input, classify, store
- [ ] Phase 3 — Library agent: 3 collections, auto-populate + manual add
- [ ] Phase 4 — Balance analyser + Planner: gap detection, hybrid planning
- [ ] Phase 5 — Nudge agent: nightly run, throttled alerts
- [ ] Phase 6 — Web dashboard: React UI
- [ ] Phase 7 — Report agent: monthly PDF
- [ ] Phase 8 — Polish: observability, retries, HITL gate

---

## Support

For support, questions, or feedback regarding CrewAI:
- Visit the [CrewAI documentation](https://docs.crewai.com)
- Reach out via the [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join the Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with the docs](https://chatg.pt/DWjSBZn)

---

## Contributing

This is a learning project demonstrating production-grade multi-agent systems. Each phase is a separate Git branch. PRs welcome.

---

## Licence

MIT
