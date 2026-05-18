from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from .journal import GrowthDomain


class ActivitySource(str, Enum):
    AI = "ai"
    PARENT = "parent"


class PlannedActivity(BaseModel):
    domain: GrowthDomain
    title: str
    description: str
    source: ActivitySource = ActivitySource.AI
    completed: bool = False


class WeeklyPlan(BaseModel):
    child_name: str
    week_start: str  # ISO date of the Monday e.g. "2026-05-18"
    focus_domains: list[GrowthDomain] = Field(default_factory=list)
    activities: list[PlannedActivity] = Field(default_factory=list)
