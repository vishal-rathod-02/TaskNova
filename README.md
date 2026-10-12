<p align="center">
  <img src="frontend/public/TaskNova.svg" alt="TaskNova Logo" width="320"/>
</p>

<p align="center">
  <strong>Modern Full-Stack Routine & Workplace Productivity Suite</strong>
</p>

<p align="center">
  <a href="https://task-nova-app.vercel.app"><img src="https://img.shields.io/badge/Live%20Demo-task--nova--app.vercel.app-6366f1?style=for-the-badge&logo=vercel&logoColor=white" alt="Live Demo"></a>
  <a href="https://tasknova-07fj.onrender.com/health"><img src="https://img.shields.io/badge/API%20Status-Live%20on%20Render-10b981?style=for-the-badge&logo=render&logoColor=white" alt="Render API"></a>
  <a href="https://github.com/vishal-rathod-02/TaskNova/releases/tag/v1.1.0"><img src="https://img.shields.io/badge/Version-v1.1.0-blue?style=for-the-badge&logo=github" alt="Version 1.1.0"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vue%203-3.5-42b883?style=flat-square&logo=vuedotjs&logoColor=white" alt="Vue 3">
  <img src="https://img.shields.io/badge/Vite-6.2-646cff?style=flat-square&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-38bdf8?style=flat-square&logo=tailwindcss&logoColor=white" alt="TailwindCSS">
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-7.0-dc382d?style=flat-square&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Celery-5.3-37814a?style=flat-square&logo=celery&logoColor=white" alt="Celery">
  <img src="https://img.shields.io/badge/JWT-Authentication-orange?style=flat-square&logo=jsonwebtokens&logoColor=white" alt="JWT">
</p>

---

## 🌐 Live Production Links

* 🖥️ **Live Web Application**: [https://task-nova-app.vercel.app](https://task-nova-app.vercel.app)
* 📦 **GitHub Repository**: [https://github.com/vishal-rathod-02/TaskNova](https://github.com/vishal-rathod-02/TaskNova)
* 🏷️ **Latest Release**: [v1.1.0](https://github.com/vishal-rathod-02/TaskNova/releases/tag/v1.1.0)

---

## 🆕 What's New in v1.1.0

* 📅 **Live RFC 5545 iCalendar Subscription**: Sync all course deadlines and assignments in real-time with Google Calendar, Apple Calendar, and Outlook via 1-click `webcal://` or private HTTPS `.ics` feeds (`/api/calendar/feed/<token>.ics`), complete with secure 32-byte cryptographic token rotation and instant revocation.
* 🖨️ **Isolated Daily Digest Print & PDF Engine**: Completely overhauled daily productivity print/PDF generation into an isolated iframe sandbox (`@page { margin: 12mm 14mm; }`), resolving 3-sheet page duplication bugs and rendering a single-page printable report with letter grades, completion velocity bars, and course breakdown tables.
* 📧 **Delta-Aware Email Notifications & Celery Pipeline**: Background daily productivity summaries now evaluate workload progress against previous reports, skipping redundant email delivery when no task activity changed. Backed by Celery worker & Celery Beat scheduling with user-configurable email preference toggles.
* 🛡️ **OWASP Security Hardening & CSV Injection Defense**: Sanitized CSV exports (`exportTasksToCSV`) against spreadsheet formula injection (DDE execution for `=`, `+`, `-`, `@`), added sliding-window auth rate limiting, JWT token revocation blocklisting, and hardened OWASP HTTP response headers.
* 📱 **Mobile-Responsive Export Dropdown**: Redesigned the "Export Ledger" dropdown in Tasks and Calendar views with smart viewport containment (`max-w-[calc(100vw-2rem)]`), eliminating layout clutter and screen clipping on small-screen devices.
* 🗄️ **Self-Healing Database Startup**: The API idempotently adds missing `user` columns (`email_digest_enabled`, `email_alerts_enabled`, `calendar_token`) on boot using native PostgreSQL `ADD COLUMN IF NOT EXISTS` inside atomic transaction blocks, plus Docker entrypoint and `Procfile` release phases, resolving `UndefinedColumn` errors on legacy databases.
* ✨ **Single-Loader UX**: Tab/view switches now render cleanly with shimmer `SkeletonLoader` transitions — removing redundant spinners across Dashboard, Courses, Tasks, Calendar, Inbox, and User Directory.
* 🔖 **Centralized Versioning**: Single source of truth in `frontend/src/version.js` (`APP_VERSION`) synchronized with `package.json`, displayed across sidebar footer, user profile menu, and authentication screens.

---

## 🚀 Unreleased: Universal Timetable & Governor Console

> On `main` after v1.1.0 — the all-in-one routine hub trajectory.

* 📅 **Universal Timetable & Plan My Day** (`/timetable`): recurring weekly blocks and one-off dated entries across five types (`meeting`, `focus_work`, `operations`, `habit`, `personal`), with collision detection, persona quick-start templates (Corporate / Maker / Campus / Freelance), and a Maker-vs-Pomodoro auto-scheduler that fits backlog tasks into free windows (preview first, apply with one click). Slots flow into the live ICS feed and support `.ics` / `.csv` export plus printable agendas.
* 🏛️ **Platform Governor Console** (`/admin`): aggregate-only metrics — signups, weekly-active users, activation and routine-adoption rates, template adoption — plus a starter-template switchboard (enable/disable with live counts) and a member/admin split directory. No per-user content is ever exposed to admins.
* 🔑 **New endpoints**: `GET/POST /api/timetable`, `PUT/DELETE /api/timetable/:id`, `POST /api/timetable/auto-schedule`, `POST /api/timetable/apply-template`, `GET /api/timetable/templates`, `GET/PATCH /api/admin/timetable/templates`.
* 🛡️ **Security posture**: `.dockerignore` files keep local `.env` files and dev state out of production images; backend dependencies are version-pinned (`requirements.txt`); routine writes are user-scoped with ownership checks and per-call creation caps.

---

## 📖 Overview

**TaskNova** is a modern, high-performance personal productivity hub engineered with **Vue 3 (Composition API), Vite, TailwindCSS, Python Flask, PostgreSQL, Redis, and Celery**.

Built for anyone who wants to organize their day in one calm place, TaskNova bridges the gap between projects, routines, daily task management, sprint-based focus habits, and automated deadline tracking in a unified daylight/night-shift interface.

---

## ✨ Key Features & Architecture

### 🎓 1. Projects & Workspace Management
* Organize work by custom projects, tags, and customizable color themes.
* Track real-time progress percentages, active workloads, and historical completion velocities.

### 📋 2. Dual Task Ledger & Interactive Kanban
* **Task Ledger**: Filterable table with priority badges, multi-project selectors, and inline quick-actions.
* **Kanban Board**: Drag-and-drop columns (`To Do`, `In Progress`, `Under Review`, `Completed`) with real-time state synchronization.
* **Subtasks & Notes**: Nested checklists with progress meters and markdown notes.

### 📅 3. Interactive Calendar (`/calendar`)
* Dedicated monthly schedule view with status rings and priority badges.
* Schedule tasks directly onto any calendar date with a single click.

### ⏱️ 4. Pomodoro Focus Timer
* 3 focus modes: **25-min Deep Focus**, **5-min Short Break**, and **15-min Long Break**.
* Micro-interactions: Live ticking countdown pills on mobile headers, amber warning states for the final 3 minutes, and pulsing rose alerts for the final 60-second sprint.

### 📊 5. Activity Heatmap & Analytics
* **12-Week Sunday-Aligned Heatmap**: GitHub-style activity rings tracking daily completions with active day inspection.
* **Animated Velocity Charts**: Interactive weekly output statistics and productivity breakdown.

### 📑 6. Print-Perfect PDF & ICS/CSV Export
* **Isolated PDF Ledger Generator**: Clean print layout with workspace metadata headers, task checklists `[ ]`, and zero website chrome clutter.
* **Universal Calendar Export**: Export directly to `.ICS` (Google/Apple Calendar) and `.CSV`.

### 🔔 7. Automated Reminders & Celery Worker
* Asynchronous 24-hour deadline scanner and daily productivity digest engine.
* Automatic in-app notification center with real-time unread badges.

### 🔐 8. Dual-Role RBAC & System Administration
* **JWT Cryptographic Auth**: 15-minute access tokens + 7-day refresh tokens with PBKDF2 password hashing and rate limiting.
* **Admin User Directory**: Administrator portal to manage accounts, inspect workloads, and toggle account access with self-deletion safeguards.
* **Governor Console & Template Switchboard**: Aggregate platform metrics plus persona-template publishing — see “Unreleased” above.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Vue 3 (Composition API), Vite, Pinia, Vue Router, TailwindCSS, Axios |
| **Backend API** | Python 3.11+, Flask REST API, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Cors |
| **WSGI Server** | Gunicorn (2 workers, 4 threads, asynchronous timeout control) |
| **Database** | PostgreSQL (Production) / SQLite (Local Dev) |
| **Caching & Message Broker** | Redis & Celery (Background task queues & scheduled beat worker) |
| **Deployment & Hosting** | Vercel (Frontend CDN), Render (Web API & Postgres), Upstash (Redis), Docker Compose |

---

## 📁 Repository Structure

```text
TaskNova/
├── docker-compose.yml              # Turnkey 1-command Docker production stack
├── README.md                       # Documentation & deployment guide
├── backend/
│   ├── run.py                      # Local application entrypoint & CLI commands
│   ├── celery_worker.py            # Celery worker process entrypoint
│   ├── requirements.txt            # Python production dependencies (includes gunicorn)
│   ├── Dockerfile                  # Production container definition for Flask (runs docker-entrypoint.sh db-sync before gunicorn)
│   ├── docker-entrypoint.sh        # Idempotent schema sync on container boot, then exec CMD
│   ├── Procfile                    # Render / Railway process definitions (includes release-phase db-sync)
│   ├── .env.example                # Backend environment configuration template
│   ├── app/
│   │   ├── __init__.py             # Flask app factory, CORS init, schema self-heal (sync_database_schema), admin auto-bootstrapper
│   │   ├── config.py               # Dynamic settings & database URL normalizer
│   │   ├── celery_app.py           # Celery beat schedules & task configuration
│   │   ├── commands.py             # CLI commands (flask db-sync, flask seed, flask run-jobs)
│   │   ├── auth/                   # JWT registration, login, and token refresh
│   │   ├── projects/               # Project & workspace management endpoints
│   │   ├── tasks/                  # Task ledger, Kanban, and subtask routes
│   │   ├── timetable/              # Routine scheduler: CRUD, auto-schedule, templates
│   │   ├── admin/                  # Admin user directory, block/delete, template governance
│   │   ├── analytics/              # Personal metrics plus aggregate governor stats
│   │   ├── notifications/          # In-app notifications & cron trigger endpoints
│   │   └── tasks_jobs/             # Asynchronous Celery reminder and digest tasks
│   │   └── models/timetable.py     # TimetableSlot, TimetableAllocation, RoutineTemplateState
│   └── tests/                      # Automated pytest API test suite (17 tests)
└── frontend/
    ├── index.html                  # HTML5 SPA entrypoint with SVG favicon
    ├── vite.config.js              # Vite configuration
    ├── vercel.json                 # SPA routing rewrites for Vercel
    ├── tailwind.config.cjs         # Design tokens & color system
    ├── public/
    │   ├── favicon.svg             # High-definition vector mortarboard & star favicon
    │   ├── TaskNova.svg            # Official brand presentation graphic
    │   └── _redirects              # SPA rewrite rule for Netlify / Render Static
    └── src/
        ├── version.js              # Single source of truth for the UI version badge (APP_VERSION)
        ├── App.vue                 # Master shell (Desktop sidebar, premium mobile tab bar, user menu)
        ├── main.js                 # App initialization & Pinia store setup
        ├── style.css               # Design system, themes & print stylesheet
        ├── api/client.js           # Axios interceptors & auto-prefixing baseURL
        ├── components/             # Reusable UI components & modals
        ├── stores/                 # Pinia state stores (auth, tasks, timer, notifications, timetable, admin)
        └── views/                  # Route views (Dashboard, Tasks, Timetable, Calendar, Admin, etc.)
```

---

## ⚡ Quick Start: Local Development

### Prerequisites
* **Python**: 3.11+
* **Node.js**: 20+
* **Redis** (Optional): Local Redis or Upstash

### 1. Backend Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app "app:create_app" db-sync   # idempotent: heals legacy DBs missing newer user columns
python run.py
```
* API Server: `http://127.0.0.1:5001`
* Health Check: `http://127.0.0.1:5001/health`

### 2. Frontend Setup
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
* Frontend SPA: `http://localhost:5173`

---

## 🐳 Turnkey Docker Deployment

To launch the entire stack with a single command:

```bash
# Clone the repository
git clone https://github.com/vishal-rathod-02/TaskNova.git
cd TaskNova

# Start all containers (Postgres, Redis, Flask API, Celery Worker, Celery Beat, Vue Frontend)
docker compose up -d --build

# Open in browser
http://localhost
```

> **Legacy database repair**: if `login`/`register` ever return `column user.email_digest_enabled does not exist`, run `flask --app "app:create_app" db-sync` (or redeploy — the Docker entrypoint and `Procfile` release phase run it automatically). Or apply the equivalent `ALTER TABLE "user" ADD COLUMN IF NOT EXISTS ...` SQL directly.

---

## 🔒 Security & Roles

TaskNova implements **Zero-Trust Role-Based Access Control (RBAC)**:

| Role | Creation | Permissions |
| :--- | :--- | :--- |
| `user` | Default on public registration (`/api/auth/register`) | Manage personal projects, routines, task ledger, focus timer, and notifications. |
| `admin` | Auto-bootstrapped via `ADMIN_EMAIL` / `ADMIN_PASSWORD` env vars | Platform governor: member directory, access control, aggregate analytics, and routine-template publishing. Never exposes per-user content. |

**Hygiene rules enforced in this repo:**

* Never commit `.env` / `.env.local` — only `.env.example` files are tracked; secrets patterns (`*.pem`, `*.key`, credential JSON) are git-ignored.
* `backend/.dockerignore` and `frontend/.dockerignore` keep local env files, virtualenvs, and dev state out of production images.
* Backend dependencies are version-pinned in `backend/requirements.txt`; the frontend builds with `npm ci` (lockfile) on Node 20+ (`engines` field).
* Change the default `ADMIN_PASSWORD` before any public deployment.

---

## 📡 API Reference Overview

| Method | Endpoint | Access | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register a new user |
| `POST` | `/api/auth/login` | Public | Sign in and obtain JWT access + refresh tokens |
| `POST` | `/api/auth/refresh` | Refresh Token | Refresh access token |
| `GET` | `/api/auth/me` | Authenticated | Fetch current profile |
| `GET/POST` | `/api/projects` | Authenticated | List or create projects |
| `GET/PUT/DELETE` | `/api/projects/:id` | Owner | Manage project details |
| `GET/POST` | `/api/tasks` | Authenticated | List with filters (status, priority, due date) or create task |
| `GET/PUT/DELETE` | `/api/tasks/:id` | Owner | Manage task |
| `POST` | `/api/tasks/:id/complete` | Owner | Quick complete task |
| `GET` | `/api/analytics/me` | Authenticated | Fetch heatmap, weekly velocity, and metrics |
| `GET` | `/api/notifications` | Authenticated | Fetch inbox notifications with unread counts |
| `GET/POST` | `/api/notifications/trigger-jobs` | Public/Cron | Execute reminder scan and daily reports |
| `GET/PATCH/DELETE` | `/api/admin/users` | Admin Only | User directory, block/unblock, and delete accounts |
| `GET/POST` | `/api/timetable` | Authenticated | List or create routine blocks (collision-checked) |
| `PUT/DELETE` | `/api/timetable/:id` | Owner | Update or delete a routine block |
| `POST` | `/api/timetable/auto-schedule` | Authenticated | Preview or apply a Maker/Pomodoro day plan |
| `POST` | `/api/timetable/apply-template` | Authenticated | Apply an enabled persona template |
| `GET` | `/api/timetable/templates` | Authenticated | List admin-enabled templates |
| `GET/PATCH` | `/api/admin/timetable/templates` | Admin Only | Template adoption stats and enable/disable |

---

## 🧪 Testing & Build Verification

```powershell
# Run backend pytest suite
cd backend
python -m pytest

# Run frontend production build
cd ..\frontend
npm run build
```

---

## 👤 Author & Acknowledgements

* **Developer**: [Vishal Rathod](https://github.com/vishal-rathod-02)
* **LinkedIn**: [Vishal Rathod](https://www.linkedin.com/in/vishalrathod02)
* **Portfolio**: [vishalrathod.tech](https://portfolio-vishal-rathod.vercel.app)
* **License**: MIT
