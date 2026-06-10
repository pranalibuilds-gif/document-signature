# Document Signature SaaS (Mini DocuSign)

## Backend Architecture
- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy (Async)
- **Migrations:** Alembic
- **Task Scheduling:** APScheduler

## Project Structure
The project follows a modular layered architecture:
- `app/core`: Infrastructure (config, database, security)
- `app/modules`: Domain features (auth, documents, etc.)
- `app/common`: Shared business primitives
- `app/utils`: Stateless helpers
- `app/jobs`: Background tasks
