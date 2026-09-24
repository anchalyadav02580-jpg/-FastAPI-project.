# Campus Lost & Found API

## 1. Project Description

A REST API that lets students report and track lost or found items on campus. It replaces
manual/informal reporting (noticeboards, group chats) with a searchable digital system:
anyone can log an item as **Lost**, **Found**, or mark it **Returned** once it's been
reclaimed, and browse/filter existing reports by status or category.

## 2. Technologies Used

- **Python 3.10+**
- **FastAPI** — web framework, request validation, auto-generated docs
- **SQLModel** — combined ORM + Pydantic schema layer over SQLAlchemy
- **SQLite** — file-based relational database
- **Uvicorn** — ASGI server

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

`lost_and_found.db` (SQLite) is created automatically on first run — no manual DB setup
required.

## 5. Swagger UI URL

```
http://127.0.0.1:8000/docs
```

(ReDoc alternative view: `http://127.0.0.1:8000/redoc`)

## 6. Available Endpoints

| Method | Path                          | Description                                          |
|--------|--------------------------------|-------------------------------------------------------|
| POST   | `/items`                      | Create a new lost/found item report                  |
| GET    | `/items`                      | List all reported items                               |
| GET    | `/items/{item_id}`            | Get a single item by ID (404 if not found)             |
| PUT    | `/items/{item_id}`            | Update an item's details/status (404 if not found)     |
| DELETE | `/items/{item_id}`            | Delete an item report (404 if not found)                |
| GET    | `/items/status/{status}`      | Filter items by status: `Lost`, `Found`, `Returned`     |
| GET    | `/items/category/{category}`  | Filter items by category (`Electronics`, `Documents`, etc.) |

**Validation rules:** `title` and `description` must be non-empty/meaningful; `status` only
accepts `Lost`, `Found`, or `Returned` (enforced via enum → automatic 422 on invalid values).

## Repository Structure

```
.
├── main.py                  # FastAPI app entrypoint, startup hook, router registration
├── app/
│   ├── database.py          # SQLite engine, create_engine(), session dependency
│   ├── models.py            # SQLModel table model + request/response schemas + validators
│   └── routers/
│       └── items.py         # All /items API routes
├── requirements.txt
├── README.md
└── screenshots/             # Proof-of-work screenshots (see screenshots/README.md)
```
