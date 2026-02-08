# Healthcare Backend Scaffold

## Tech Stack
- Python 3.11
- Flask + Flask-RESTX
- SQLAlchemy + Alembic
- PostgreSQL
- Redis
- Celery
- S3-compatible storage (MinIO)
- Docker + Docker Compose

## Modules
- Authentication
- Patient
- Doctor
- Device
- Medical Data
- Alerts
- Consent
- Security
- Audit
- Retention
- API Docs

## Quick Start
1. Copy `.env` from `.env.example` (if present) and update secrets.
2. Run `docker-compose up --build` to start all services.
3. Access API at `http://localhost:5000/`.

## Structure
- `app/` - Main application code
- `migrations/` - Alembic migrations
- `Dockerfile`, `docker-compose.yml` - Containerization
