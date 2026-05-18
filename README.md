# Rooted and Rising

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

## Tech stack

| Layer | Technology |
|-------|-----------|
| Agent framework | [CrewAI](https://crewai.com) |
| LLM | Claude (Anthropic API) |
| Database | SQLite + SQLModel |
| PDF generation | WeasyPrint + Jinja2 |
| Logging | structlog |
| Config | pydantic-settings |
| Testing | pytest + pytest-asyncio |
| Package management | uv |

---

## Project structure

```
rooted-and-rising/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── uv.lock
├── .gitignore
├── data/                        # SQLite database
├── knowledge/                   # Agent knowledge files
└── src/
    └── rooted_and_rising_crew/
        ├── config/
        │   ├── agents.yaml      # Agent definitions
        │   └── tasks.yaml       # Task definitions
        ├── models/              # Pydantic data contracts
        ├── tools/               # Custom tools
        ├── crew.py              # Crew wiring
        ├── database.py          # DB setup
        ├── main.py              # Entry point
        └── repository.py        # Data access layer
```

---

## Getting started

### Prerequisites
- Python 3.12+
- `uv` (Python package manager)

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/rooted-and-rising.git
cd rooted-and-rising

# Install dependencies
crewai install

# Add your Anthropic API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run the crew
crewai run
```

### Customising agents and tasks

- Edit `src/rooted_and_rising_crew/config/agents.yaml` to configure agents
- Edit `src/rooted_and_rising_crew/config/tasks.yaml` to configure tasks
- Edit `src/rooted_and_rising_crew/crew.py` to add tools or custom logic

---

## Common commands

```bash
crewai run              # interactive parent session
crewai install          # install / sync dependencies
crewai train            # train the crew
crewai test             # run tests
crewai replay           # replay a previous run
rm -f data/rooted.db    # reset the database
sqlite3 data/rooted.db  # open database shell
```

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

## Licence

MIT
