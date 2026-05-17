"""
Data access layer — all reads and writes to the SQLite database.

Functions here translate between the SQLModel row types (persistence) and the
Pydantic agent-contract models (domain). Nothing outside this module touches
the DB models directly.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

from sqlmodel import Session, select

from rooted_and_rising_crew.models.analysis import GapReport
from rooted_and_rising_crew.models.db import (
    ActivityItemRow,
    BookItemRow,
    FoodItemRow,
    JournalEntryRow,
    PlannedActivityRow,
    WeeklyPlanRow,
)
from rooted_and_rising_crew.models.journal import GrowthDomain, JournalEntry
from rooted_and_rising_crew.models.library import LibraryExtraction
from rooted_and_rising_crew.models.planning import WeeklyPlan

_DOMAIN_LABELS = {
    GrowthDomain.ACADEMICS: "Academics & Reading  ",
    GrowthDomain.OUTDOOR:   "Outdoor & Health     ",
    GrowthDomain.VALUES:    "Values & Religious Ed",
    GrowthDomain.FAMILY:    "Family & Friends     ",
    GrowthDomain.CREATIVE:  "Creative Pursuits    ",
}


# ── Journal entries ───────────────────────────────────────────────────────────

def save_journal_entry(session: Session, entry: JournalEntry) -> JournalEntryRow:
    row = JournalEntryRow(
        child_name=entry.child_name,
        date=entry.date,
        domain=entry.domain.value,
        summary=entry.summary,
        raw_text=entry.raw_text,
        tags_json=json.dumps(entry.tags),
        library_candidates_json=json.dumps(entry.library_candidates),
    )
    session.add(row)
    session.flush()  # populate row.id without committing yet
    return row


def get_domain_history(
    session: Session,
    child_name: str,
    window_days: int = 7,
) -> str:
    """
    Compute the formatted domain-history string the balance analyser expects,
    derived from real stored journal entries.

    Format per line:
        - academics: 2 days ago (3 entries in window)
        - outdoor: never (0 entries in window)
    """
    today = date.today()
    cutoff = (today - timedelta(days=window_days)).isoformat()
    lines: list[str] = []

    for domain in GrowthDomain:
        # Most recent entry across all time for this domain
        recent_stmt = (
            select(JournalEntryRow)
            .where(JournalEntryRow.child_name == child_name)
            .where(JournalEntryRow.domain == domain.value)
            .order_by(JournalEntryRow.date.desc())  # type: ignore[arg-type]
            .limit(1)
        )
        recent = session.exec(recent_stmt).first()

        # Entries within the rolling window
        window_stmt = (
            select(JournalEntryRow)
            .where(JournalEntryRow.child_name == child_name)
            .where(JournalEntryRow.domain == domain.value)
            .where(JournalEntryRow.date >= cutoff)
        )
        window_entries = session.exec(window_stmt).all()
        count = len(window_entries)
        entry_word = "entry" if count == 1 else "entries"

        if recent is None:
            lines.append(f"- {domain.value}: never (0 entries in window)")
        else:
            days_ago = (today - date.fromisoformat(recent.date)).days
            unit = "day" if days_ago == 1 else "days"
            lines.append(
                f"- {domain.value}: {days_ago} {unit} ago ({count} {entry_word} in window)"
            )

    return "\n".join(lines)


def get_recent_entries(
    session: Session,
    child_name: str,
    limit: int = 20,
) -> list[JournalEntryRow]:
    stmt = (
        select(JournalEntryRow)
        .where(JournalEntryRow.child_name == child_name)
        .order_by(JournalEntryRow.date.desc())  # type: ignore[arg-type]
        .limit(limit)
    )
    return list(session.exec(stmt).all())


# ── Library items ─────────────────────────────────────────────────────────────

def save_library_items(
    session: Session,
    child_name: str,
    items: LibraryExtraction,
) -> None:
    """Upsert library items — skip duplicates by title/name + child."""
    today = date.today().isoformat()

    existing_books = {
        r.title.lower()
        for r in session.exec(
            select(BookItemRow).where(BookItemRow.child_name == child_name)
        ).all()
    }
    for book in items.books:
        if book.title.lower() not in existing_books:
            session.add(BookItemRow(
                child_name=child_name,
                title=book.title,
                author=book.author,
                genre=book.genre,
                domain=book.domain.value,
                status=book.status.value,
                added_date=today,
            ))

    existing_foods = {
        r.name.lower()
        for r in session.exec(
            select(FoodItemRow).where(FoodItemRow.child_name == child_name)
        ).all()
    }
    for food in items.foods:
        if food.name.lower() not in existing_foods:
            session.add(FoodItemRow(
                child_name=child_name,
                name=food.name,
                category=food.category,
                status=food.status.value,
                added_date=today,
            ))

    existing_activities = {
        r.name.lower()
        for r in session.exec(
            select(ActivityItemRow).where(ActivityItemRow.child_name == child_name)
        ).all()
    }
    for activity in items.activities:
        if activity.name.lower() not in existing_activities:
            session.add(ActivityItemRow(
                child_name=child_name,
                name=activity.name,
                domain=activity.domain.value,
                status=activity.status.value,
                added_date=today,
            ))


# ── Weekly plans ──────────────────────────────────────────────────────────────

def save_weekly_plan(session: Session, plan: WeeklyPlan) -> WeeklyPlanRow:
    plan_row = WeeklyPlanRow(
        child_name=plan.child_name,
        week_start=plan.week_start,
        focus_domains_json=json.dumps([d.value for d in plan.focus_domains]),
        created_date=date.today().isoformat(),
    )
    session.add(plan_row)
    session.flush()

    for act in plan.activities:
        session.add(PlannedActivityRow(
            plan_id=plan_row.id,  # type: ignore[arg-type]
            domain=act.domain.value,
            title=act.title,
            description=act.description,
            source=act.source.value,
            completed=act.completed,
        ))

    return plan_row


# ── Summary helpers ───────────────────────────────────────────────────────────

def get_library_summary(session: Session, child_name: str) -> dict[str, int]:
    """Return counts of books, foods, activities for a child."""
    return {
        "books": len(session.exec(
            select(BookItemRow).where(BookItemRow.child_name == child_name)
        ).all()),
        "foods": len(session.exec(
            select(FoodItemRow).where(FoodItemRow.child_name == child_name)
        ).all()),
        "activities": len(session.exec(
            select(ActivityItemRow).where(ActivityItemRow.child_name == child_name)
        ).all()),
    }
