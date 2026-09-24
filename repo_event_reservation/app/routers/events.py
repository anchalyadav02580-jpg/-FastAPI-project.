"""
API routes for events.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status as http_status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Event, EventCreate, EventUpdate

router = APIRouter(prefix="/events", tags=["Events"])


def get_event_or_404(event_id: int, session: Session) -> Event:
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=f"Event with id {event_id} not found")
    return event


@router.post("", response_model=Event, status_code=http_status.HTTP_201_CREATED)
def create_event(event: EventCreate, session: Session = Depends(get_session)):
    """Create a new event."""
    db_event = Event(**event.model_dump())
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router.get("", response_model=List[Event])
def read_events(session: Session = Depends(get_session)):
    """Return all events."""
    return session.exec(select(Event)).all()


@router.get("/{event_id}", response_model=Event)
def read_event(event_id: int, session: Session = Depends(get_session)):
    """Return a specific event by ID."""
    return get_event_or_404(event_id, session)


@router.put("/{event_id}", response_model=Event)
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


@router.delete("/{event_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, session: Session = Depends(get_session)):
    """Delete an event."""
    db_event = get_event_or_404(event_id, session)
    session.delete(db_event)
    session.commit()
    return None
