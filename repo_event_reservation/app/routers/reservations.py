"""
API routes for reservations, tied to a parent event, plus availability
and cancellation.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status as http_status
from sqlmodel import Session, select, func

from app.database import get_session
from app.models import Event, Reservation, ReservationCreate, EventStatus, AvailabilityResponse
from app.routers.events import get_event_or_404

router = APIRouter(tags=["Reservations"])


def count_reservations(event_id: int, session: Session) -> int:
    result = session.exec(
        select(func.count(Reservation.id)).where(Reservation.event_id == event_id)
    ).one()
    return result or 0


@router.post(
    "/events/{event_id}/reserve",
    response_model=Reservation,
    status_code=http_status.HTTP_201_CREATED,
)
def create_reservation(event_id: int, reservation: ReservationCreate, session: Session = Depends(get_session)):
    """
    Create a reservation for an event.

    Checks, in order:
    1. Event exists (404 if not).
    2. Event is Open (400 if Closed).
    3. Event is not full (400 if booked >= capacity).
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


@router.get("/events/{event_id}/reservations", response_model=List[Reservation])
def read_event_reservations(event_id: int, session: Session = Depends(get_session)):
    """Return all reservations for a particular event."""
    get_event_or_404(event_id, session)
    return session.exec(select(Reservation).where(Reservation.event_id == event_id)).all()


@router.get("/events/{event_id}/availability", response_model=AvailabilityResponse)
def read_event_availability(event_id: int, session: Session = Depends(get_session)):
    """Return capacity, booked, and remaining seat counts for an event."""
    event = get_event_or_404(event_id, session)
    booked = count_reservations(event_id, session)
    remaining = max(event.capacity - booked, 0)
    return AvailabilityResponse(capacity=event.capacity, booked=booked, remaining=remaining)


@router.delete("/reservations/{reservation_id}", status_code=http_status.HTTP_204_NO_CONTENT)
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
