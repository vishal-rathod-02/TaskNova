# TaskNova - Smart Task & Productivity Management System

TaskNova is a full-stack productivity app built with Flask + Vue.

## Included Features

- JWT auth (register, login, refresh, current user)
- Role-based access (`user`, `admin`)
- Projects CRUD
- Tasks CRUD with deadlines, priority and completion flow
- Task activity logs
- Admin user management (list users, block/unblock, delete non-admin users)
- Analytics dashboard APIs
- Redis caching for dashboard stats
- Celery background task hooks (deadline reminders and daily reports)

## Stack

- Backend: Flask, SQLAlchemy, JWT, Redis, Celery
- Frontend: Vue 3, Pinia, Vue Router, Axios, Vite
- DB: SQLite by default (switchable to PostgreSQL via `DATABASE_URL`)

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
flask --app run.py shell
```

Initialize DB and seed admin:

```bash
cd backend
flask --app run.py shell -c "from app.extensions import db; db.create_all()"
flask --app run.py seed
python run.py
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`, backend on `http://127.0.0.1:5001`.

## Celery + Redis (Optional Runtime)

Start Redis (local install or Docker), then:

```bash
cd backend
celery -A app.tasks.celery worker --loglevel=info
```

You can later schedule periodic jobs via Celery Beat for:

- `send_deadline_reminders`
- `generate_daily_productivity_report`
