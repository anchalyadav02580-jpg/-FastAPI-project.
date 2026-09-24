"""
Campus Lost & Found API — application entrypoint.
"""

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import items

app = FastAPI(
    title="Campus Lost & Found API",
    description="Report, track, and resolve lost/found items on campus.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(items.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Campus Lost & Found API is running. Visit /docs for Swagger UI."}
