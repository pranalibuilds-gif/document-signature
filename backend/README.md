# Document Signature SaaS (Mini DocuSign)

## Backend Architecture
- **Framework:** FastAPI
- **Database:** SQLite local development default, PostgreSQL optional for production-style environments
- **Migrations:** Alembic
- **Task Scheduling:** APScheduler

## Local setup
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --reload
```

### Troubleshooting
If imports fail with `ModuleNotFoundError: No module named 'app'`, ensure the backend venv is activated before running tests or the API server:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

## Project Structure
The project follows a modular layered architecture:
- `app/core`: Infrastructure (config, database, security)
- `app/modules`: Domain features (auth, documents, etc.)
- `app/common`: Shared business primitives
- `app/utils`: Stateless helpers
- `app/jobs`: Background tasks
