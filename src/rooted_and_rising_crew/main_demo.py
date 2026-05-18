#!/usr/bin/env python
"""
Rooted and Rising — hardcoded demo run (no prompts).

Uses a fixed journal entry for Aryan but still reads domain history from
SQLite (so repeated demo runs accumulate realistic context) and saves
all results back to the database.

Useful for CI, smoke-testing, and first-run demonstrations.

Usage:
    make demo
    .venv/bin/python -m rooted_and_rising_crew.main_demo
"""
from __future__ import annotations

import json
import sys
import warnings
from datetime import date, timedelta

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from rooted_and_rising_crew.crew import RootedAndRisingCrew
from rooted_and_rising_crew.database import create_db_and_tables, get_session
from rooted_and_rising_crew.models import GapReport, JournalEntry, LibraryExtraction, WeeklyPlan
from rooted_and_rising_crew.repository import (
    get_domain_history,
    get_library_summary,
    save_journal_entry,
    save_library_items,
    save_weekly_plan,
)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# ── Demo fixtures ─────────────────────────────────────────────────────────────

_DEMO_CHILD = "Aryan"

_DEMO_JOURNAL = (
    "Aryan finished his maths homework really quickly today and then spent an hour "
    "reading 'The Magic Faraway Tree' by Enid Blyton. He was so excited that he "
    "re-told me the whole first chapter at dinner!"
)

# Kept for train/test entry points that need a fully self-contained inputs dict
_DEMO_HISTORY = """- academics: 1 day ago (3 entries in window)
- outdoor: 9 days ago (0 entries in window)
- values: 5 days ago (1 entry in window)
- family: 2 days ago (2 entries in window)
- creative: 11 days ago (0 entries in window)"""


def _monday_of_week(today: date) -> str:
    return (today - timedelta(days=today.weekday())).isoformat()


def _build_inputs(
    child_name: str,
    journal_text: str,
    domain_history: str,
) -> dict[str, str]:
    today = date.today()
    return {
        "child_name": child_name,
        "journal_text": journal_text,
        "current_date": today.isoformat(),
        "window_days": "7",
        "domain_history": domain_history,
        "week_start": _monday_of_week(today),
    }


# ── Flow ─────────────────────────────────────────────────────────────────────

class GrowthState(BaseModel):
    child_name: str = _DEMO_CHILD
    journal_text: str = _DEMO_JOURNAL
    domain_history: str = ""
    journal_entry: JournalEntry | None = None
    library_items: LibraryExtraction | None = None
    gap_report: GapReport | None = None
    weekly_plan: WeeklyPlan | None = None


class GrowthFlow(Flow[GrowthState]):

    @start()
    def run_crew(self) -> None:
        inputs = _build_inputs(
            self.state.child_name,
            self.state.journal_text,
            self.state.domain_history,
        )
        result = RootedAndRisingCrew().crew().kickoff(inputs=inputs)

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
    def save_to_db(self) -> None:
        with get_session() as session:
            if self.state.journal_entry:
                save_journal_entry(session, self.state.journal_entry)
            if self.state.library_items:
                save_library_items(
                    session, self.state.child_name, self.state.library_items
                )
            if self.state.weekly_plan:
                save_weekly_plan(session, self.state.weekly_plan)
            lib_counts = get_library_summary(session, self.state.child_name)

        print(
            f"  📁 Saved to log  "
            f"(📚 {lib_counts['books']} books · "
            f"🍎 {lib_counts['foods']} foods · "
            f"⚽ {lib_counts['activities']} activities total)\n"
        )

    @listen(save_to_db)
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
                icon = (
                    "✅" if ds.status.value == "balanced"
                    else ("⚠️ " if ds.status.value == "low" else "🔴")
                )
                print(
                    f"  {icon} {ds.domain.value:<12} {ds.status.value:<10} "
                    f"({ds.last_activity_days_ago}d ago, {ds.entry_count} entries)"
                )
            print(f"\n  {g.summary}")

        if self.state.weekly_plan:
            p = self.state.weekly_plan
            print(f"\n📅 WEEKLY PLAN  (week of {p.week_start})")
            for i, act in enumerate(p.activities, 1):
                print(f"\n  {i}. [{act.domain.value.upper()}] {act.title}")
                print(f"     {act.description}")

        print("\n" + "═" * 60 + "\n")


# ── Entry points ──────────────────────────────────────────────────────────────

def run() -> None:
    create_db_and_tables()
    with get_session() as session:
        domain_history = get_domain_history(session, _DEMO_CHILD)
    flow = GrowthFlow()
    flow.state.domain_history = domain_history
    flow.kickoff()


def run_with_trigger() -> None:
    if len(sys.argv) < 2:
        raise ValueError("No trigger payload provided. Pass JSON as argument.")
    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON payload: {e}") from e

    create_db_and_tables()
    child_name = payload.get("child_name", _DEMO_CHILD)
    journal_text = payload.get("journal_text", _DEMO_JOURNAL)

    with get_session() as session:
        domain_history = payload.get(
            "domain_history",
            get_domain_history(session, child_name),
        )

    flow = GrowthFlow()
    flow.state.child_name = child_name
    flow.state.journal_text = journal_text
    flow.state.domain_history = domain_history
    flow.kickoff()


if __name__ == "__main__":
    run()
