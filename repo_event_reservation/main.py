"""
College Event Reservation API — application entrypoint.
"""

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import events, reservations

app = FastAPI(
    title="College Event Reservation API",
    description="Manage events and student reservations with seat-capacity enforcement.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(events.router)
app.include_router(reservations.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "College Event Reservation API is running. Visit /docs for Swagger UI."}
