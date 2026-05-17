from __future__ import annotations

from pydantic import BaseModel, Field

from .journal import GrowthDomain


class DomainHighlight(BaseModel):
    domain: GrowthDomain
    summary: str
    entry_count: int
    highlights: list[str] = Field(default_factory=list)


class MonthlyReport(BaseModel):
    child_name: str
    month: str  # "YYYY-MM"
    domain_highlights: list[DomainHighlight] = Field(default_factory=list)
    overall_summary: str
    milestones: list[str] = Field(default_factory=list)
