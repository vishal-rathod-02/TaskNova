# TaskNova

TaskNova is a smart task and productivity management system for individuals and small teams. Flask serves a JSON API; Vue 3 + Tailwind provides the Daylight Ledger SPA.

## User roles

There are 2 roles (`backend/app/models/user.py:14`, enforced by `role_required` in `backend/app/utils/auth.py:24`):

| Role | How it is created | What it can do |
| --- | --- | --- |
| `user` | Default for every `POST /api/auth/register` | Own projects/tasks, personal dashboard, task activity |
| `admin` | Seeded via `flask --app run.py seed`, never via public register | Everything above system-wide, plus `GET/PATCH/DELETE /api/admin/users` and `/api/analytics/admin` |

Admins cannot be blocked or deleted through the admin API. Blocked users cannot log in.

## Repository layout

```text
TaskNova/
  README.md
  backend/
    run.py
    celery_worker.py
    requirements.txt
    .env.example
    tests/
    app/
      __init__.py
      config.py
      extensions.py
      celery_app.py
      auth/
      projects/
      tasks/
      admin/
      analytics/
      notifications/ # inbox API for persisted job output
      tasks_jobs/
      models/
      utils/
  frontend/
    index.html
    vite.config.js
    tailwind.config.cjs
    postcss.config.cjs
    .env.example
    src/
      main.js
      style.css
      router/
      api/client.js
      services/      # auth, projects, tasks, admin, analytics, notifications
      stores/        # auth, projects, tasks, analytics, admin, notifications
      components/    # PageHeader, EmptyState, FormField, TaskLedgerRow, AppIcon, ToastNotifications, UserMenu, AppErrorBoundary
      composables/   # toast, useTheme
      views/         # Login, Register, Dashboard, Projects, Tasks, Admin, Notifications, NotFound
```

Only source is committed. Local artifacts stay untracked via `.gitignore`:

- `frontend/node_modules/`, `frontend/dist/` — reinstall/rebuild with npm
- `backend/.venv/`, `__pycache__/`, `.pytest_cache/`, `backend/instance/`, `backend/uploads/`, `backend/celerybeat-schedule*`, `*.db`
- Root and service `.env` files — copy from `.env.example`

`frontend/dist/` is a rebuildable artifact and is not kept in the workspace.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Redis optional; API and UI work without it, caching/reminders degrade gracefully

## Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

API: `http://127.0.0.1:5001`, health: `http://127.0.0.1:5001/health`.

Configure `backend/.env` from `.env.example`: `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`, token TTLs, dashboard TTLs, `REMINDER_WINDOW_HOURS`, `AUTO_CREATE_DB`.

`CORS_ORIGINS` must list each frontend origin exactly, with no trailing slash — e.g. `http://localhost:5173,http://127.0.0.1:5173`. A missing or slashed entry makes the browser block API calls with `No 'Access-Control-Allow-Origin' header`. After changing it, or after any backend code change, restart `python run.py`.

Seed the admin account:

```powershell
flask --app run.py seed
```

Dev admin: `admin@tasknova.com` / `admin123`. Change it outside local development.

## Frontend setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

SPA: `http://localhost:5173`. `VITE_API_BASE_URL` defaults to `http://127.0.0.1:5001/api`.

Sign in as admin with the seeded credentials; the `Admin` navigation appears only for `role === "admin"`.

## Optional Redis and Celery

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A celery_worker.celery worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info
```

Beat schedules deadline reminders every 15 minutes and the daily productivity report at 00:05 UTC. Both jobs persist their output: reminders and the per-user report land in the notification inbox (`/notifications` view, unread badge in the sidebar), and the report is also readable at `GET /api/analytics/report/latest` with history at `/report/history`. On Windows run the worker with `--pool=solo`.

## Stale dev database

`AUTO_CREATE_DB` only creates missing tables — it never alters existing ones. After pulling model changes, a dev database from older code can cause `sqlite3.OperationalError: no such column: ...`. Repair it by dropping just the stale table (your projects and tasks are untouched), then restart the backend so the current schema is recreated:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -c "from app import create_app; app = create_app(); ctx = app.app_context(); ctx.push(); from app.extensions import db; from sqlalchemy import text; db.session.execute(text('DROP TABLE IF EXISTS notification')); db.session.commit(); db.create_all()"
python run.py
```

(`flask shell` in this project has no `-c` flag, so the repair runs through `python -c` with an explicit app context instead.)

## Validation

```powershell
cd backend
python -m pytest -q

cd ..\frontend
npm run build
```

## Core API

| Method | Path | Access |
| --- | --- | --- |
| POST | `/api/auth/register` | Public, always creates `user` |
| POST | `/api/auth/login` | Public |
| POST | `/api/auth/refresh` | Refresh token |
| GET | `/api/auth/me` | Authenticated |
| GET/POST | `/api/projects` | Owner |
| GET/PUT/DELETE | `/api/projects/:id` | Owner |
| GET/POST | `/api/projects/:id/tasks` | Owner |
| GET/POST | `/api/tasks` | Owner, filterable + paginated |
| GET/PUT/DELETE | `/api/tasks/:id` | Owner |
| POST | `/api/tasks/:id/complete` | Owner |
| GET | `/api/tasks/:id/activity` | Owner |
| GET | `/api/analytics/me` | Authenticated |
| GET | `/api/analytics/report/latest` | Owner, latest persisted daily report |
| GET | `/api/analytics/report/history` | Owner, up to 30 persisted daily reports |
| GET | `/api/notifications` | Owner, filterable with `unread_only` and `kind` |
| POST | `/api/notifications/:id/read` | Owner |
| POST | `/api/notifications/read-all` | Owner |
| GET/PATCH/DELETE | `/api/admin/users`, `/api/admin/users/:id/block`, `/api/admin/users/:id` | `admin` only |
| GET | `/api/analytics/admin` | `admin` only |
