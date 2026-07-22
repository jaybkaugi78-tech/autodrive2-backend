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

Runs on `http://localhost:5000`. The `car_marketplace.db` SQLite file and
all tables are created automatically on first run.

## Endpoints

| Method | Route | Protected | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create an account |
| POST | `/auth/login` | No | Log in, returns JWT |
| POST | `/auth/reset-password` | No | Request a reset token |
| PUT | `/auth/reset-password/<token>` | No | Set a new password |
| GET | `/cars` | No | List all cars |
| GET | `/cars/<id>` | No | Get one car |
| POST | `/cars` | Yes | Post a new car |
| PUT | `/cars/<id>` | Yes | Update your own car |
| DELETE | `/cars/<id>` | Yes | Delete your own car |
| GET | `/favorites` | Yes | List your favorited cars |
| POST | `/favorites` | Yes | Favorite a car |
| DELETE | `/favorites/<id>` | Yes | Remove a favorite |
| GET | `/admin/users` | Yes (admin) | List every user |
| DELETE | `/admin/users/<id>` | Yes (admin) | Delete any user (cascades their listings) |
| DELETE | `/admin/cars/<id>` | Yes (admin) | Delete any listing, not just your own |

Protected routes require `Authorization: Bearer <token>`.

## Creating an admin account

Public registration can only create `buyer`/`seller` accounts — admin can't
be self-assigned through the API. Create or promote one from the command line:

```bash
python create_admin.py admin@example.com "Admin Name" somepassword
```

Run this after the database exists (i.e. after `python app.py` has run
once, or against your deployed Postgres database with `DATABASE_URL` set).

## Models

- `User` — id, name, email, password_hash, role, created_at
- `Car` — id, make, model, year, price, mileage, seller_id (FK → User)
- `Listing` — id, car_id (FK → Car), description, status, date_posted
- `Favorite` — id, user_id (FK → User), car_id (FK → Car) — join table

Relationships: `User → Car` and `Car → Listing` (one-to-many),
`User ↔ Car` via `Favorite` (many-to-many).

## Notes

- Password reset tokens are time-limited (30 min) and signed with `itsdangerous`.
  `POST /auth/reset-password` returns the token directly in the response for
  local testing — in a real deployment this would be emailed instead.
- CORS is restricted to `CORS_ORIGINS` in `.env` — add your deployed frontend
  URL there before going live.

## Deploying to Vercel

Vercel runs Flask as a serverless function, and its filesystem is wiped
between requests — so SQLite won't persist. This repo is set up for
**Vercel Postgres** (Neon-backed), which plugs in with almost no config.

1. **Create the database**: in your Vercel project → Storage tab →
   Create Database → Postgres. Vercel auto-generates a `DATABASE_URL`
   and can inject it into your project's env vars for you.
2. **Set environment variables** in Vercel → Settings → Environment Variables:
   - `DATABASE_URL` (from step 1, or paste it manually)
   - `SECRET_KEY` — any random string
   - `JWT_SECRET_KEY` — a different random string
   - `CORS_ORIGINS` — your deployed frontend URL, e.g. `https://your-app.vercel.app`
3. **Deploy**: push this repo to GitHub, then import it in Vercel. It reads
   `vercel.json`, which routes all requests through `api/index.py` (the
   serverless entrypoint wrapping the Flask app in `app.py`).
4. Once live, update your frontend's `REACT_APP_API_URL` to the deployed
   backend URL and redeploy the frontend.

Locally, nothing changes — no `DATABASE_URL` set means it falls back to
SQLite automatically (see `config.py`).
