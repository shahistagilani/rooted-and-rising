"""
SQLModel table definitions — the persistence layer.

These are intentionally separate from the Pydantic agent-contract models
in the sibling modules. The agent contracts are the domain language; these
are the storage representation. Mapping between the two lives in repository.py.

JSON-encoded list columns (tags_json, etc.) use plain strings because SQLite
has no native array type. repository.py handles encoding/decoding.
"""
from __future__ import annotations

from sqlmodel import Field, SQLModel


class JournalEntryRow(SQLModel, table=True):
    __tablename__ = "journal_entries"

    id: int | None = Field(default=None, primary_key=True)
    child_name: str = Field(index=True)
    date: str                    # ISO date  "YYYY-MM-DD"
    domain: str                  # GrowthDomain value
    summary: str
    raw_text: str
    tags_json: str = Field(default="[]")               # JSON list[str]
    library_candidates_json: str = Field(default="[]") # JSON list[str]


class BookItemRow(SQLModel, table=True):
    __tablename__ = "book_items"

    id: int | None = Field(default=None, primary_key=True)
    child_name: str = Field(index=True)
    title: str
    author: str = ""
    genre: str = ""
    domain: str = "academics"
    status: str = "tried"
    added_date: str = ""         # ISO date, set on insert


class FoodItemRow(SQLModel, table=True):
    __tablename__ = "food_items"

    id: int | None = Field(default=None, primary_key=True)
    child_name: str = Field(index=True)
    name: str
    category: str = ""
    status: str = "tried"
    added_date: str = ""


class ActivityItemRow(SQLModel, table=True):
    __tablename__ = "activity_items"

    id: int | None = Field(default=None, primary_key=True)
    child_name: str = Field(index=True)
    name: str
    domain: str
    status: str = "tried"
    added_date: str = ""


class WeeklyPlanRow(SQLModel, table=True):
    __tablename__ = "weekly_plans"

    id: int | None = Field(default=None, primary_key=True)
    child_name: str = Field(index=True)
    week_start: str              # ISO date of the Monday
    focus_domains_json: str = Field(default="[]")  # JSON list[str]
    created_date: str = ""


class PlannedActivityRow(SQLModel, table=True):
    __tablename__ = "planned_activities"

    id: int | None = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="weekly_plans.id", index=True)
    domain: str
    title: str
    description: str
    source: str = "ai"           # "ai" | "parent"
    completed: bool = False
