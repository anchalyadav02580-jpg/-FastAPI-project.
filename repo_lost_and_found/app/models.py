"""
SQLModel table models and Pydantic-style request/response schemas
for the Lost & Found API.
"""

from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field
from pydantic import field_validator


class ItemStatus(str, Enum):
    LOST = "Lost"
    FOUND = "Found"
    RETURNED = "Returned"


class ItemCategory(str, Enum):
    ELECTRONICS = "Electronics"
    DOCUMENTS = "Documents"
    ACCESSORIES = "Accessories"
    CLOTHING = "Clothing"
    BOOKS = "Books"
    OTHER = "Other"


# ---------------------------------------------------------------------------
# Table model
# ---------------------------------------------------------------------------
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1)
    description: str
    category: ItemCategory
    location: str
    reported_by: str
    status: ItemStatus = Field(default=ItemStatus.LOST)


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class ItemCreate(SQLModel):
    title: str
    description: str
    category: ItemCategory
    location: str
    reported_by: str
    status: ItemStatus = ItemStatus.LOST

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_must_be_meaningful(cls, v: str) -> str:
        if not v or len(v.strip()) < 5:
            raise ValueError("description must contain meaningful text (min 5 characters)")
        return v.strip()

    @field_validator("location")
    @classmethod
    def location_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("location must not be empty")
        return v.strip()

    @field_validator("reported_by")
    @classmethod
    def reported_by_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("reported_by must not be empty")
        return v.strip()


class ItemUpdate(SQLModel):
    """All fields optional — PUT only changes fields the client actually sends."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ItemCategory] = None
    location: Optional[str] = None
    reported_by: Optional[str] = None
    status: Optional[ItemStatus] = None

    @field_validator("title")
    @classmethod
    def title_not_empty_if_given(cls, v):
        if v is not None and not v.strip():
            raise ValueError("title must not be empty")
        return v.strip() if v else v

    @field_validator("description")
    @classmethod
    def description_meaningful_if_given(cls, v):
        if v is not None and len(v.strip()) < 5:
            raise ValueError("description must contain meaningful text (min 5 characters)")
        return v.strip() if v else v
