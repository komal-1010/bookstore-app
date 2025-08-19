
## 1) Backend README (Django + DRF)

### 🧭 Overview

Minimal e‑commerce backend for a **book store**. Provides JWT auth, product & category management, cart, orders, Stripe Checkout, webhooks, and Celery task for confirmation email.

### 🧱 Tech Stack

* Django 4 / Django REST Framework
* PostgreSQL (DB name: **boostore**)
* Redis (Celery broker & cache)
* Celery (async tasks)
* Stripe (Checkout + webhook)
* SimpleJWT (access/refresh tokens)
* Docker & docker-compose (optional)

## 🚀 Quick Start (Local, no Docker)

### 0) Prerequisites

* Python 3.11+
* PostgreSQL 13+
* Redis 6+
* Stripe account & API keys

### 1) Clone & enter

```bash
git clone <your-backend-repo-url> backend
cd backend
```

### 2) Create & activate venv

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3) Install deps

```bash
pip install -r requirements.txt
```

### 4) Create `.env`

Create a `.env` file in the project root (same folder as `manage.py`).

```env
# Django
DJANGO_SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS (add your frontend URL in prod)
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000

# Postgres
DB_NAME=boostore
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

> **Note:** In production (Render), set these in the dashboard environment variables and update `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` with your real domains.

### 5) Create DB & run migrations

Make sure a Postgres database named **boostore** exists (or let Django create tables):

```bash
createdb boostore  # or create via pgAdmin
python manage.py migrate
```

### 6) (Optional) Seed sample book data

We include a management command to seed categories/products:

```bash
python manage.py seed_books
```

If you don’t see the command, use fixtures instead:

```bash
python manage.py loaddata fixtures/books.json
```

### 7) Run server

```bash
python manage.py runserver 0.0.0.0:8000
```

### 8) Start Celery (optional but recommended)

Open **two terminals**:

```bash
# Terminal A – worker
celery -A backend worker -l info

# Terminal B – beat (if you schedule tasks)
celery -A backend beat -l info
```

### 9) Stripe webhook for local dev

Install Stripe CLI and run:

```bash
stripe login
stripe listen --forward-to http://localhost:8000/api/payments/webhooks/stripe/
```

Copy the **Signing secret** it prints and set it as `STRIPE_WEBHOOK_SECRET` in `.env`.

---

## 🐳 Docker Setup (Backend)

### 1) `.env` (same as above)

Ensure the `.env` exists.

### 2) Build & run

```bash
docker compose up --build
```

This starts:

* `web` (Django)
* `db` (Postgres)
* `redis`
* `worker` (Celery)
* `beat` (Celery Beat)

Run migrations inside the web container (first time):

```bash
docker compose exec web python manage.py migrate
```

Seed data (optional):

```bash
docker compose exec web python manage.py seed_books
```

Expose ports as defined in your `docker-compose.yml` (commonly 8000 for Django).

---
