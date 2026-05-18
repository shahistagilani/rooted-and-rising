from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from .journal import GrowthDomain


class CoverageStatus(str, Enum):
    BALANCED = "balanced"
    LOW = "low"
    NEGLECTED = "neglected"


class DomainScore(BaseModel):
    domain: GrowthDomain
    last_activity_days_ago: int
    entry_count: int
    status: CoverageStatus


class GapReport(BaseModel):
    child_name: str
    window_days: int
    domain_scores: list[DomainScore] = Field(default_factory=list)
    neglected_domains: list[GrowthDomain] = Field(default_factory=list)
    summary: str
