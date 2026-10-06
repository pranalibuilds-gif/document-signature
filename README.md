# Northstar Sign

Northstar Sign is a local-first document-signing application built with FastAPI, SQLAlchemy, Alembic, SQLite, and Next.js. It supports account management, document uploads, signer and field setup, signing links, audit history, and generated signed PDFs.

This repository is intended for local development and portfolio/demo use. No hosting or paid services are required to run the core application.

## Requirements

- Python 3.12
- Node.js 20 or newer and npm 10 or newer
- Windows PowerShell instructions are shown below; equivalent commands work on other platforms with the appropriate virtual-environment activation command.

## First-time setup

### 1. Configure the backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `backend/.env` and replace the example `SECRET_KEY` with a random value of at least 32 characters. The default configuration uses SQLite at `backend/local_dev.db`; PostgreSQL is optional.

Initialize the database and populate the demo data:

```powershell
python -m alembic upgrade head
python -m scripts.seed_demo_data
```

> **Warning:** The demo seed script clears existing application records before creating its sample dataset. Use it only with a disposable local/demo database. It is disabled when `ENVIRONMENT=production`.

The seed script creates sample accounts, document records, signer assignments, audit history, and synthetic PDFs under `backend/storage/`. The SQLite database and generated storage files are intentionally ignored by Git, so repeat these setup steps after cloning to recreate the demo locally.

### 2. Start the backend

Keep the backend virtual environment active:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend API: <http://localhost:8000>
Interactive API documentation: <http://localhost:8000/docs>

### 3. Start the frontend

Open a second terminal at the repository root:

```powershell
cd frontend
npm ci
npm run dev
```

If PowerShell blocks npm scripts, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then retry.

Frontend: <http://localhost:3000>

The Next.js development server proxies `/api/*` requests to the local backend at `http://127.0.0.1:8000`.

## Demo accounts

The seed script creates these local demo accounts:

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@northstar-tech.com` | `admin123` |
| User | `pranali@northstar-tech.com` | `northstar2025` |

These are public demo credentials for a disposable local database only. Do not use them, or the seeded passwords, for a public or production deployment.

## Checks

Backend tests and lint:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
python -m ruff check app tests scripts
```

Frontend lint and production build:

```powershell
cd frontend
npm run lint
npm run build
```

## Project layout

- `backend/app/core`: application configuration, database, authentication, and middleware
- `backend/app/modules`: auth, documents, signers, fields, signing, notifications, audit, users, and admin features
- `backend/alembic`: database migrations
- `backend/scripts/seed_demo_data.py`: local synthetic demo-data generator
- `frontend/src/app`: Next.js routes
- `frontend/src/modules`: document editor and signing UI

## Data and configuration notes

- `backend/local_dev.db`, `backend/storage/`, and `.env` files are local-only and are not tracked by Git.
- Running Alembic migrations creates the schema; run the seed script separately if you want the demo accounts and sample documents.
- Set `DATABASE_URL` in `backend/.env` to use a PostgreSQL URL instead of SQLite.
- Configure a real email provider in `backend/.env` if you want invitations or account emails delivered. Mock email is intended only for local testing.

## License

This project is for educational and portfolio purposes. All rights reserved.
