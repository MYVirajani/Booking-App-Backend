# Playground Booking - Backend

FastAPI backend for an indoor playground/court booking system (netball, cricket, tennis courts, etc.)
with PayHere payment integration and PostgreSQL-enforced double-booking prevention.

## Stack
- **FastAPI** + SQLAlchemy 2.0
- **PostgreSQL** with a GiST exclusion constraint that prevents overlapping bookings at the database level, even under concurrent requests
- **Alembic** for migrations
- **JWT** auth (phone + password)
- **PayHere** payment gateway (LKR), with server-to-server webhook confirmation
- **APScheduler** for expiring unpaid booking holds every minute

## Prerequisites
- Python 3.11+
- PostgreSQL 14+ running locally or reachable via `DATABASE_URL`
- A PayHere sandbox account (free) — see "PayHere setup" below

## Project structure

```
app/
├── main.py              # FastAPI app entrypoint, router + scheduler wiring
├── core/                 # config, DB session, JWT/password utils, auth dependency
├── models/                 # SQLAlchemy models (User, Court, Booking, Payment)
├── schemas/                  # Pydantic request/response shapes
├── routers/                    # auth, courts, bookings, payments
├── services/                      # booking overlap logic, PayHere hash/signature logic
└── background/                       # scheduled job that expires unpaid holds
alembic/                                # DB migrations (0001 creates the overlap constraint)
```

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in real values, see below
```

Create the database and enable the extension the overlap constraint needs:

```sql
CREATE DATABASE playground_booking;
\c playground_booking
CREATE EXTENSION IF NOT EXISTS btree_gist;
```

Run migrations:

```bash
alembic upgrade head
```

Run the server (from the project root — the folder containing `app/`, not inside it):

```bash
uvicorn app.main:app --reload
```

- Health check: `http://localhost:8000/health`
- Interactive API docs: `http://localhost:8000/docs`

## Environment variables (`.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `SECRET_KEY` | Random secret used to sign JWTs |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime (default 1440 = 24h) |
| `PAYHERE_MERCHANT_ID` | From your PayHere sandbox/live account |
| `PAYHERE_MERCHANT_SECRET` | App-specific secret from PayHere's Domains & Credentials page |
| `PAYHERE_SANDBOX` | `true` for testing, `false` for real payments |
| `BOOKING_HOLD_MINUTES` | How long a `pending` booking holds a slot before auto-cancelling |

## PayHere setup (sandbox)

1. Sign up at sandbox.payhere.lk — free, no business verification needed for sandbox.
2. Settings → Domains and Credentials → copy your **Merchant ID**.
3. Add your Flutter app's package name as an "App" entry, request approval (usually instant for sandbox), and copy the resulting **Merchant Secret**.
4. For local webhook testing, run `ngrok http 8000` and point `notify_url` in `app/routers/payments.py` at the ngrok URL — PayHere calls your webhook server-to-server, so `localhost` won't work.


## Testing the core guarantee

The most important thing to verify is that the same court can never be double-booked, even under concurrent requests:

```bash
# Run the same booking request twice for the same court/time
curl -X POST http://localhost:8000/bookings -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"court_id":"<id>","start_time":"2026-09-24T14:00:00Z","end_time":"2026-09-24T15:00:00Z"}'
```

First call → `201 Created`. Second call → `409 Conflict`. If both succeed, the exclusion constraint didn't get created — check that `alembic upgrade head` ran and `btree_gist` is enabled.
