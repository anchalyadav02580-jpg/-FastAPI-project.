# Screenshots

Place your proof-of-work screenshots here, one per required case:

1. `01_post_events.png` — POST /events
2. `02_get_events.png` — GET /events
3. `03_successful_reservation.png` — POST /events/{id}/reserve (success)
4. `04_get_event_reservations.png` — GET /events/{id}/reservations
5. `05_event_availability.png` — GET /events/{id}/availability
6. `06_cancel_reservation.png` — DELETE /reservations/{id}
7. `07_reservation_rejected_full.png` — reservation attempt on a full event (400)
8. `08_reservation_rejected_closed.png` — reservation attempt on a closed event (400)

Each screenshot should clearly show the endpoint/URL, request body (if any), and the
response body + status code. Using the Swagger UI at `/docs` captures all three at once.
For #7/#8, first fill the event to capacity or set its status to `Closed`, then show the
rejected attempt — the "before" state proves the business logic is actually running.
