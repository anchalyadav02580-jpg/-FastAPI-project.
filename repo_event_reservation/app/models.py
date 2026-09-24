"""
SQLModel table models and request/response schemas for the
Event Reservation API.
"""

from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field
from pydantic import field_validator, EmailStr


class EventStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"


# ---------------------------------------------------------------------------
# Table models
# ---------------------------------------------------------------------------
class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    venue: str
    capacity: int
    organizer: str
    status: EventStatus = Field(default=EventStatus.OPEN)


class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    student_name: str
    roll_number: str
    email: str


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class EventCreate(SQLModel):
    title: str
    venue: str
    capacity: int
    organizer: str
    status: EventStatus = EventStatus.OPEN

    @field_validator("title", "venue", "organizer")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("field must not be empty")
        return v.strip()

    @field_validator("capacity")
    @classmethod
    def capacity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("capacity must be greater than 0")
        return v


class EventUpdate(SQLModel):
    title: Optional[str] = None
    venue: Optional[str] = None
    capacity: Optional[int] = None
    organizer: Optional[str] = None
    status: Optional[EventStatus] = None

    @field_validator("capacity")
    @classmethod
    def capacity_positive_if_given(cls, v):
        if v is not None and v <= 0:
            raise ValueError("capacity must be greater than 0")
        return v

    @field_validator("title", "venue", "organizer")
    @classmethod
    def not_empty_if_given(cls, v):
        if v is not None and not v.strip():
            raise ValueError("field must not be empty")
        return v.strip() if v else v


class ReservationCreate(SQLModel):
    student_name: str
    roll_number: str
    email: EmailStr

    @field_validator("student_name")
    @classmethod
    def student_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("student_name must not be empty")
        return v.strip()

    @field_validator("roll_number")
    @classmethod
    def roll_number_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("roll_number must not be empty")
        return v.strip()


class AvailabilityResponse(SQLModel):
    capacity: int
    booked: int
    remaining: int
