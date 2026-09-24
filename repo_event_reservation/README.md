# College Event Reservation API

## 1. Project Description

A REST API for managing college events (workshops, hackathons, seminars) and student
reservations. It replaces manual seat-tracking with an automated system that enforces
event capacity and prevents reservations against closed or fully-booked events, while
letting organizers view live seat availability at any time.

## 2. Technologies Used

- **Python 3.10+**
- **FastAPI** — web framework, request validation, auto-generated docs
- **SQLModel** — combined ORM + Pydantic schema layer over SQLAlchemy
- **SQLite** — file-based relational database
- **Uvicorn** — ASGI server
- **Pydantic `EmailStr`** — email format validation

## 3. Installation Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 4. Command to Run the FastAPI Application

```bash
uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

`events.db` (SQLite) is created automatically on first run — no manual DB setup required.

## 5. Swagger UI URL

```
http://127.0.0.1:8000/docs
```

(ReDoc alternative view: `http://127.0.0.1:8000/redoc`)

## 6. Available Endpoints

### Events

| Method | Path                  | Description                                  |
|--------|------------------------|------------------------------------------------|
| POST   | `/events`             | Create a new event                            |
| GET    | `/events`             | List all events                               |
| GET    | `/events/{event_id}`  | Get a single event by ID (404 if not found)     |
| PUT    | `/events/{event_id}`  | Update event info (404 if not found)            |
| DELETE | `/events/{event_id}`  | Delete an event (404 if not found)              |

### Reservations

| Method | Path                                | Description                                                              |
|--------|--------------------------------------|----------------------------------------------------------------------------|
| POST   | `/events/{event_id}/reserve`        | Reserve a seat — rejects with 400 if event is closed or full, 404 if event doesn't exist |
| GET    | `/events/{event_id}/reservations`   | List all reservations for an event                                        |
| GET    | `/events/{event_id}/availability`   | Return `{capacity, booked, remaining}`                                    |
| DELETE | `/reservations/{reservation_id}`    | Cancel a reservation (404 if not found)                                    |

**Validation rules:** `capacity` must be > 0; `student_name` and `roll_number` must be
non-empty; `email` must be a valid email format (enforced via `EmailStr`); reservations
must reference an existing `event_id`.

**Business logic:** every reservation attempt checks, in order — event exists → event is
`Open` → current booked count < `capacity` — before any row is written, so overbooking and
reservations on closed events are both impossible by construction, not just convention.

## Repository Structure

```
.
├── main.py                     # FastAPI app entrypoint, startup hook, router registration
├── app/
│   ├── database.py             # SQLite engine, create_engine(), session dependency
│   ├── models.py                # SQLModel table models + request/response schemas + validators
│   └── routers/
│       ├── events.py            # /events CRUD routes
│       └── reservations.py      # /events/{id}/reserve, /reservations, availability
├── requirements.txt
├── README.md
└── screenshots/                 # Proof-of-work screenshots (see screenshots/README.md)
```
