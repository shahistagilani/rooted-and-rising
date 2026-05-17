#!/usr/bin/env python
"""
Rooted and Rising — entry points for crewai CLI and direct invocation.

Demo run pipeline:
  journal entry → classify → extract library items → analyse balance → plan week
"""
from __future__ import annotations

import json
import sys
import warnings
from datetime import date, timedelta

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from rooted_and_rising_crew.crew import RootedAndRisingCrew
from rooted_and_rising_crew.models import GapReport, JournalEntry, LibraryExtraction, WeeklyPlan

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# ── Sample domain history for demo (simulates 7-day rolling window) ──────────
_DEMO_HISTORY = """- academics: 1 day ago (3 entries in window)
- outdoor: 9 days ago (0 entries in window)
- values: 5 days ago (1 entry in window)
- family: 2 days ago (2 entries in window)
- creative: 11 days ago (0 entries in window)"""

_DEMO_JOURNAL = (
    "Aryan finished his maths homework really quickly today and then spent an hour "
    "reading 'The Magic Faraway Tree' by Enid Blyton. He was so excited that he "
    "re-told me the whole first chapter at dinner!"
)


def _monday_of_week(today: date) -> str:
    return (today - timedelta(days=today.weekday())).isoformat()


def _build_inputs(child_name: str, journal_text: str) -> dict[str, str]:
    today = date.today()
    return {
        "child_name": child_name,
        "journal_text": journal_text,
        "current_date": today.isoformat(),
        "window_days": "7",
        "domain_history": _DEMO_HISTORY,
        "week_start": _monday_of_week(today),
    }


# ── Flow ─────────────────────────────────────────────────────────────────────

class GrowthState(BaseModel):
    child_name: str = "Aryan"
    journal_text: str = _DEMO_JOURNAL
    journal_entry: JournalEntry | None = None
    library_items: LibraryExtraction | None = None
    gap_report: GapReport | None = None
    weekly_plan: WeeklyPlan | None = None


class GrowthFlow(Flow[GrowthState]):

    @start()
    def run_crew(self) -> None:
        inputs = _build_inputs(self.state.child_name, self.state.journal_text)
        result = RootedAndRisingCrew().crew().kickoff(inputs=inputs)

        # Pull typed outputs from each task in the sequential pipeline
        task_outputs = result.tasks_output
        if len(task_outputs) >= 1 and task_outputs[0].pydantic:
            self.state.journal_entry = task_outputs[0].pydantic  # type: ignore[assignment]
        if len(task_outputs) >= 2 and task_outputs[1].pydantic:
            self.state.library_items = task_outputs[1].pydantic  # type: ignore[assignment]
        if len(task_outputs) >= 3 and task_outputs[2].pydantic:
            self.state.gap_report = task_outputs[2].pydantic  # type: ignore[assignment]
        if len(task_outputs) >= 4 and task_outputs[3].pydantic:
            self.state.weekly_plan = task_outputs[3].pydantic  # type: ignore[assignment]

    @listen(run_crew)
    def display_results(self) -> None:
        print("\n" + "═" * 60)
        print("  🌱 ROOTED AND RISING — RESULTS")
        print("═" * 60)

        if self.state.journal_entry:
            e = self.state.journal_entry
            print(f"\n📖 JOURNAL ENTRY")
            print(f"  Child   : {e.child_name}")
            print(f"  Date    : {e.date}")
            print(f"  Domain  : {e.domain.value.upper()}")
            print(f"  Summary : {e.summary}")
            print(f"  Tags    : {', '.join(e.tags)}")
            if e.library_candidates:
                print(f"  Spotted : {', '.join(e.library_candidates)}")

        if self.state.library_items:
            lib = self.state.library_items
            print(f"\n📚 LIBRARY ITEMS EXTRACTED")
            for b in lib.books:
                print(f"  [Book]     {b.title}" + (f" by {b.author}" if b.author else ""))
            for f in lib.foods:
                print(f"  [Food]     {f.name}")
            for a in lib.activities:
                print(f"  [Activity] {a.name} ({a.domain.value})")
            if not (lib.books or lib.foods or lib.activities):
                print("  (no named items extracted)")

        if self.state.gap_report:
            g = self.state.gap_report
            print(f"\n📊 BALANCE REPORT ({g.window_days}-day window)")
            for ds in g.domain_scores:
                icon = "✅" if ds.status.value == "balanced" else ("⚠️ " if ds.status.value == "low" else "🔴")
                print(f"  {icon} {ds.domain.value:<12} {ds.status.value:<10} ({ds.last_activity_days_ago}d ago, {ds.entry_count} entries)")
            print(f"\n  {g.summary}")

        if self.state.weekly_plan:
            p = self.state.weekly_plan
            print(f"\n📅 WEEKLY PLAN  (week of {p.week_start})")
            for i, act in enumerate(p.activities, 1):
                print(f"\n  {i}. [{act.domain.value.upper()}] {act.title}")
                print(f"     {act.description}")

        print("\n" + "═" * 60 + "\n")


# ── crewai CLI entry points ───────────────────────────────────────────────────

def run() -> None:
    GrowthFlow().kickoff()


def train() -> None:
    inputs = _build_inputs("Aryan", _DEMO_JOURNAL)
    try:
        RootedAndRisingCrew().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise RuntimeError(f"Training failed: {e}") from e


def replay() -> None:
    try:
        RootedAndRisingCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise RuntimeError(f"Replay failed: {e}") from e


def test() -> None:
    inputs = _build_inputs("Aryan", _DEMO_JOURNAL)
    try:
        RootedAndRisingCrew().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise RuntimeError(f"Test failed: {e}") from e


def run_with_trigger() -> None:
    if len(sys.argv) < 2:
        raise ValueError("No trigger payload provided. Pass JSON as argument.")
    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON payload: {e}") from e

    child_name = payload.get("child_name", "Aryan")
    journal_text = payload.get("journal_text", _DEMO_JOURNAL)

    flow = GrowthFlow()
    flow.state.child_name = child_name
    flow.state.journal_text = journal_text
    flow.kickoff()
