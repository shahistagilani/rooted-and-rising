from __future__ import annotations

from pydantic import BaseModel

from .journal import GrowthDomain


class NudgeMessage(BaseModel):
    domain: GrowthDomain
    message: str
    days_since_last_activity: int
    suggested_activity: str
