# Car Marketplace — Backend

Flask REST API for the Car Marketplace capstone project.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit the secrets
python app.py
```

Runs on `http://localhost:5000`. The SQLite database and all tables are
created automatically on first run (no `DATABASE_URL` needed locally).

## Seed sample data

Want the browse page to have something in it right away instead of
starting empty?

```bash
python seed.py
```

Creates a demo seller account and 9 sample cars with full specs and
placeholder images. Safe to run more than once — it skips seeding if
any cars already exist.

## Creating an admin account

Public registration can only create `buyer`/`seller` accounts — admin
can't be self-assigned through the API. Create or promote one from the
command line:

```bash
python create_admin.py admin@example.com "Admin Name" somepassword
```

If the email already exists, that account is promoted to admin. Run
this against your production database by prefixing with `DATABASE_URL`
(see Deploying below).

## Endpoints

| Method | Route | Protected | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create an account (buyer or seller) |
| POST | `/auth/login` | No | Log in, returns JWT |
| POST | `/auth/reset-password` | No | Request a reset token |
| PUT | `/auth/reset-password/<token>` | No | Set a new password |
| GET | `/cars` | No | List all cars |
| GET | `/cars/<id>` | No | Get one car |
| POST | `/cars` | Yes (seller/admin) | Post a new car listing |
| PUT | `/cars/<id>` | Yes (owner/admin) | Update a car |
| DELETE | `/cars/<id>` | Yes (owner/admin) | Delete a car |
| GET | `/favorites` | Yes | List your favorited cars |
| POST | `/favorites` | Yes | Favorite a car |
| DELETE | `/favorites/<id>` | Yes | Remove a favorite |
| POST | `/cars/<id>/messages` | No | Buyer messages the car's seller |
| GET | `/messages` | Yes | Seller's inbox — messages about their cars |
| DELETE | `/messages/<id>` | Yes (recipient) | Delete a received message |
| GET | `/admin/users` | Yes (admin) | List every user |
| DELETE | `/admin/users/<id>` | Yes (admin) | Delete any user (cascades their listings) |
| DELETE | `/admin/cars/<id>` | Yes (admin) | Delete any listing, not just your own |

Protected routes require `Authorization: Bearer <token>`.

## Models

- `User` — id, name, email, password_hash, role (buyer/seller/admin), created_at
- `Car` — id, make, model, year, price, mileage, image_url, seller_id (FK → User),
  plus optional specs: fuel_type, transmission, horsepower, engine, drivetrain,
  seats, zero_to_hundred, weight_kg, fuel_consumption, description
- `Listing` — id, car_id (FK → Car), description, status, date_posted
- `Favorite` — id, user_id (FK → User), car_id (FK → Car) — join table
- `CarMessage` — id, car_id (FK → Car), seller_id (FK → User), buyer_name,
  buyer_email, message, created_at — a buyer's inquiry about a specific car,
  delivered to that car's seller only

Relationships: `User → Car` and `Car → Listing` (one-to-many),
`User ↔ Car` via `Favorite` (many-to-many).

## Access control

- Anyone can browse cars and view details — no login required.
- Only accounts with `role = seller` (or `admin`) can post a car listing.
  Registering asks the user to pick "Browse & buy" (buyer) or "Sell cars"
  (seller) — the role can't be self-assigned as `admin`.
- A seller can only edit/delete their own listings; an admin can edit/delete
  any listing.
- Anyone (logged in or not) can message a car's seller via
  `POST /cars/<id>/messages` — no account needed to send an inquiry.
- Only the seller who owns a car sees messages about it, via `GET /messages`.

## Validation & serialization

Every request is validated and every response is built with
**Marshmallow** (`schemas.py`) — no manual `if` checks or hand-built
dicts. Invalid input returns `400` with a structured
`{"error": {"field": ["reason"]}}` body. Enum-style fields (`fuel_type`,
`transmission`, `drivetrain`, registration `role`) are restricted to
known valid values.

## Notes

- Password reset tokens are time-limited (30 min) and signed with
  `itsdangerous`. `POST /auth/reset-password` returns the token directly
  in the response for local testing — in a real deployment this would be
  emailed instead. **The confirm step (setting a new password with that
  token) has no frontend page yet** — the backend endpoint works, but
  there's currently no UI to use it.
- CORS is restricted to `CORS_ORIGINS` in `.env` — set this to your
  deployed frontend URL before going live.

## Deploying

This backend can run on either Render or Vercel; both are supported.

### Render (recommended — runs Flask as a normal process)

1. Push this repo to GitHub.
2. Create a Postgres database on Render (free tier is fine).
3. Create a Web Service from this repo:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Set environment variables: `DATABASE_URL` (from the Postgres instance),
   `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS` (your frontend's URL).
5. Deploy. Tables are created automatically on first run.

### Vercel (serverless)

Uses `vercel.json` and `api/index.py` to run Flask as a serverless
function. Needs a hosted Postgres database too (Vercel Postgres/Neon,
since Vercel's filesystem is ephemeral and SQLite won't persist).
Same environment variables as above. Note: Vercel's Python/Flask
support is community-maintained and can be less predictable than
Render for a long-lived API like this one.

Locally, nothing changes either way — no `DATABASE_URL` set falls back
to SQLite automatically (see `config.py`).