from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from .journal import GrowthDomain


class ItemStatus(str, Enum):
    TRIED = "tried"
    ENJOYS = "enjoys"
    MASTERED = "mastered"
    LOVES = "loves"
    DISLIKES = "dislikes"


class BookItem(BaseModel):
    title: str
    author: str = ""
    genre: str = ""
    domain: GrowthDomain = GrowthDomain.ACADEMICS
    status: ItemStatus = ItemStatus.TRIED


class FoodItem(BaseModel):
    name: str
    category: str = ""
    status: ItemStatus = ItemStatus.TRIED


class ActivityItem(BaseModel):
    name: str
    domain: GrowthDomain
    status: ItemStatus = ItemStatus.TRIED


class LibraryExtraction(BaseModel):
    books: list[BookItem] = Field(default_factory=list)
    foods: list[FoodItem] = Field(default_factory=list)
    activities: list[ActivityItem] = Field(default_factory=list)
