from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class GrowthDomain(str, Enum):
    ACADEMICS = "academics"
    OUTDOOR = "outdoor"
    VALUES = "values"
    FAMILY = "family"
    CREATIVE = "creative"


class MediaAttachment(BaseModel):
    file_path: str
    media_type: str  # "image" | "audio"


class RawInput(BaseModel):
    child_name: str
    text: str
    images: list[str] = Field(default_factory=list)
    audio_path: str | None = None


class JournalEntry(BaseModel):
    child_name: str
    date: str  # ISO date string e.g. "2026-05-17"
    domain: GrowthDomain
    summary: str
    raw_text: str
    tags: list[str] = Field(default_factory=list)
    library_candidates: list[str] = Field(default_factory=list)
    media: list[MediaAttachment] = Field(default_factory=list)
