#!/usr/bin/env python
"""
Rooted and Rising — live interactive entry point.

Prompts the parent for their child's name and today's journal entry,
loads the rolling domain history from SQLite, runs the full agent
pipeline, saves all results back to the database, then prints a
formatted summary.

Usage:
    crewai run          (from rooted_and_rising_crew/ directory)
    make run            (from repo root)
    .venv/bin/python -m rooted_and_rising_crew.main
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


# ── Input helpers ─────────────────────────────────────────────────────────────

def _prompt(label: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    value = input(f"  {label}{hint}: ").strip()
    return value or default


def _prompt_multiline(label: str) -> str:
    print(f"  {label}")
    print("  (type your entry below; press Enter on an empty line when done)\n")
    lines: list[str] = []
    while True:
        line = input("  > ")
        if line == "":
            if lines:
                break
            print("  (please write something first, then press Enter on an empty line)")
        else:
            lines.append(line)
    return " ".join(lines)


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


def _collect_inputs() -> tuple[str, str]:
    """
    Prompt the parent for child name and today's journal entry.
    Returns (child_name, journal_text).
    Domain history is loaded from the database — no manual entry needed.
    """
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         🌱  ROOTED AND RISING  —  Child Co-pilot         ║")
    print("║           Grounded in values. Growing every day.         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    print("─── Step 1 of 2: Child's name ───────────────────────────")
    child_name = _prompt("Child's name", default="")
    while not child_name:
        print("  Name cannot be empty.")
        child_name = _prompt("Child's name", default="")

    print()
    print("─── Step 2 of 2: Today's journal entry ──────────────────")
    print(f"  What did {child_name} do today? Be as natural as you like —")
    print("  mention books read, food tried, games played, anything!\n")
    journal_text = _prompt_multiline("Journal entry:")

    print()
    print(f"  ✓  Got it! Loading {child_name}'s history and running analysis...")
    print("  (This takes about 30–60 seconds)\n")

    return child_name, journal_text


# ── Flow ─────────────────────────────────────────────────────────────────────

class GrowthState(BaseModel):
    child_name: str = ""
    journal_text: str = ""
    domain_history: str = ""   # populated from DB before kickoff
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


# ── crewai CLI entry points ───────────────────────────────────────────────────

def run() -> None:
    """crewai run → interactive parent session backed by SQLite."""
    create_db_and_tables()
    child_name, journal_text = _collect_inputs()

    with get_session() as session:
        domain_history = get_domain_history(session, child_name)

    flow = GrowthFlow()
    flow.state.child_name = child_name
    flow.state.journal_text = journal_text
    flow.state.domain_history = domain_history
    flow.kickoff()


def train() -> None:
    from rooted_and_rising_crew.main_demo import (
        _DEMO_CHILD,
        _DEMO_HISTORY,
        _DEMO_JOURNAL,
        _build_inputs as _demo_build,
    )
    inputs = _demo_build(_DEMO_CHILD, _DEMO_JOURNAL, _DEMO_HISTORY)
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
    from rooted_and_rising_crew.main_demo import (
        _DEMO_CHILD,
        _DEMO_HISTORY,
        _DEMO_JOURNAL,
        _build_inputs as _demo_build,
    )
    inputs = _demo_build(_DEMO_CHILD, _DEMO_JOURNAL, _DEMO_HISTORY)
    try:
        RootedAndRisingCrew().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs,
        )
    except Exception as e:
        raise RuntimeError(f"Test failed: {e}") from e


def run_with_trigger() -> None:
    """Non-interactive entry point for programmatic/trigger invocation."""
    if len(sys.argv) < 2:
        raise ValueError("No trigger payload provided. Pass JSON as argument.")
    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON payload: {e}") from e

    create_db_and_tables()
    child_name = payload.get("child_name", "")
    journal_text = payload.get("journal_text", "")

    if not child_name or not journal_text:
        raise ValueError("Payload must include 'child_name' and 'journal_text'.")

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
