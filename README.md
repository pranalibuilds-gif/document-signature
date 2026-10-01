# Northstar Sign - Enterprise Document Workflow SaaS

Northstar Sign is a full-stack document signature platform designed for secure organizational workflows. It is structured as a local-first, zero-cost development project with optional PostgreSQL support for production-style environments.

---

## Local development status

This project is configured to run without Docker or a paid database setup in local development.

- Backend defaults to SQLite via `sqlite+aiosqlite:///./local_dev.db`
- PostgreSQL remains available as an optional override when `DATABASE_URL` or `POSTGRES_*` values are set
- Frontend runs with the standard Next.js dev flow

---

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Troubleshooting
If `pytest` or `uvicorn` reports `ModuleNotFoundError: No module named 'app'`, activate the backend virtual environment first:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

### Optional demo seed
```bash
cd backend
.\.venv\Scripts\python.exe scripts/seed_demo_data.py
```

---

## Architecture

### Backend
- FastAPI
- SQLAlchemy async ORM
- Alembic migrations
- SQLite local fallback with optional PostgreSQL

### Frontend
- Next.js App Router
- Tailwind CSS
- Type-safe client patterns

---

## Notes

This project is suitable for local development and portfolio/demo validation without paying for infrastructure. Production deployment is intentionally left out of scope here.

---

## License
This project is for educational and portfolio purposes. All rights reserved.
