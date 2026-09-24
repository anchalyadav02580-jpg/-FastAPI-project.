"""
Event Reservation API
----------------------
FastAPI + SQLModel + SQLite backend for managing college events
(workshops, hackathons, seminars) and student reservations, with
seat-capacity enforcement.
"""

from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends, status as http_status
from sqlmodel import SQLModel, Field, Session, create_engine, select, func
from pydantic import field_validator, EmailStr


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./events.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
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
# Request/response schemas
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


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="College Event Reservation API",
    description="Manage events and student reservations with seat-capacity enforcement.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_event_or_404(event_id: int, session: Session) -> Event:
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=f"Event with id {event_id} not found")
    return event


def count_reservations(event_id: int, session: Session) -> int:
    result = session.exec(
        select(func.count(Reservation.id)).where(Reservation.event_id == event_id)
    ).one()
    return result or 0


# ---------------------------------------------------------------------------
# Event routes
# ---------------------------------------------------------------------------
@app.post("/events", response_model=Event, status_code=http_status.HTTP_201_CREATED, tags=["Events"])
def create_event(event: EventCreate, session: Session = Depends(get_session)):
    """Create a new event."""
    db_event = Event(**event.model_dump())
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@app.get("/events", response_model=List[Event], tags=["Events"])
def read_events(session: Session = Depends(get_session)):
    """Return all events."""
    return session.exec(select(Event)).all()


@app.get("/events/{event_id}", response_model=Event, tags=["Events"])
def read_event(event_id: int, session: Session = Depends(get_session)):
    """Return a specific event by ID."""
    return get_event_or_404(event_id, session)


@app.put("/events/{event_id}", response_model=Event, tags=["Events"])
def update_event(event_id: int, event_update: EventUpdate, session: Session = Depends(get_session)):
    """Update an existing event's information."""
    db_event = get_event_or_404(event_id, session)
    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@app.delete("/events/{event_id}", status_code=http_status.HTTP_204_NO_CONTENT, tags=["Events"])
def delete_event(event_id: int, session: Session = Depends(get_session)):
    """Delete an event."""
    db_event = get_event_or_404(event_id, session)
    session.delete(db_event)
    session.commit()
    return None


# ---------------------------------------------------------------------------
# Reservation routes
# ---------------------------------------------------------------------------
@app.post(
    "/events/{event_id}/reserve",
    response_model=Reservation,
    status_code=http_status.HTTP_201_CREATED,
    tags=["Reservations"],
)
def create_reservation(
    event_id: int, reservation: ReservationCreate, session: Session = Depends(get_session)
):
    """
    Create a reservation for an event.

    Order of checks:
    1. Event must exist (404 if not).
    2. Event must be Open (400 if Closed).
    3. Event must not be full (400 if booked count >= capacity).
    """
    event = get_event_or_404(event_id, session)

    if event.status != EventStatus.OPEN:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Event '{event.title}' is closed and not accepting reservations",
        )

    booked = count_reservations(event_id, session)
    if booked >= event.capacity:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Event '{event.title}' is fully booked ({booked}/{event.capacity})",
        )

    db_reservation = Reservation(event_id=event_id, **reservation.model_dump())
    session.add(db_reservation)
    session.commit()
    session.refresh(db_reservation)
    return db_reservation


@app.get(
    "/events/{event_id}/reservations",
    response_model=List[Reservation],
    tags=["Reservations"],
)
def read_event_reservations(event_id: int, session: Session = Depends(get_session)):
    """Return all reservations for a particular event."""
    get_event_or_404(event_id, session)  # ensures event exists
    return session.exec(select(Reservation).where(Reservation.event_id == event_id)).all()


@app.get(
    "/events/{event_id}/availability",
    response_model=AvailabilityResponse,
    tags=["Reservations"],
)
def read_event_availability(event_id: int, session: Session = Depends(get_session)):
    """Return capacity, booked, and remaining seat counts for an event."""
    event = get_event_or_404(event_id, session)
    booked = count_reservations(event_id, session)
    remaining = max(event.capacity - booked, 0)
    return AvailabilityResponse(capacity=event.capacity, booked=booked, remaining=remaining)


@app.delete(
    "/reservations/{reservation_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    tags=["Reservations"],
)
def cancel_reservation(reservation_id: int, session: Session = Depends(get_session)):
    """Cancel (delete) a reservation by ID."""
    db_reservation = session.get(Reservation, reservation_id)
    if not db_reservation:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with id {reservation_id} not found",
        )
    session.delete(db_reservation)
    session.commit()
    return None
