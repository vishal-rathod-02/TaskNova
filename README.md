<p align="center">
  <img src="frontend/public/TaskNova.svg" alt="TaskNova Logo" width="320"/>
</p>

<p align="center">
  <strong>Modern Full-Stack Academic Task & Workplace Productivity Suite</strong>
</p>

<p align="center">
  <a href="https://task-nova-app.vercel.app"><img src="https://img.shields.io/badge/Live%20Demo-task--nova--app.vercel.app-6366f1?style=for-the-badge&logo=vercel&logoColor=white" alt="Live Demo"></a>
  <a href="https://tasknova-api-odp5.onrender.com/health"><img src="https://img.shields.io/badge/API%20Status-Live%20on%20Render-10b981?style=for-the-badge&logo=render&logoColor=white" alt="Render API"></a>
  <a href="https://github.com/vishal-rathod-02/TaskNova"><img src="https://img.shields.io/badge/Version-v1.0.0-blue?style=for-the-badge&logo=github" alt="Version 1.0"></a>
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
* ⚡ **Production REST API**: [https://tasknova-api-odp5.onrender.com](https://tasknova-api-odp5.onrender.com)
* 📦 **GitHub Repository**: [https://github.com/vishal-rathod-02/TaskNova](https://github.com/vishal-rathod-02/TaskNova)

---

## 📖 Overview

**TaskNova** is a modern, high-performance academic productivity workspace engineered with **Vue 3 (Composition API), Vite, TailwindCSS, Python Flask, PostgreSQL, Redis, and Celery**. 

Built specifically for students, researchers, and educators, TaskNova bridges the gap between course syllabi, daily task management, sprint-based study habits, and automated deadline tracking in a unified daylight/night-shift interface.

---

## ✨ Key Features & Architecture

### 🎓 1. Academic Courses & Syllabi Management
* Organize coursework by custom course codes, credit weights, instructor details, and customizable color themes.
* Track real-time progress percentages, active assignment workloads, and historical completion velocities.

### 📋 2. Dual Task Ledger & Interactive Kanban
* **Task Ledger**: Filterable table with priority badges, multi-course selectors, and inline quick-actions.
* **Kanban Board**: Drag-and-drop columns (`To Do`, `In Progress`, `Under Review`, `Completed`) with real-time state synchronization.
* **Subtasks & Notes**: Nested checklists with progress meters and markdown notes.

### 📅 3. Interactive Academic Calendar (`/calendar`)
* Dedicated monthly academic schedule view with status rings and priority badges.
* Schedule tasks directly onto any calendar date with a single click.

### ⏱️ 4. Pomodoro Study Focus Timer
* 3 study modes: **25-min Study Focus**, **5-min Short Break**, and **15-min Long Break**.
* Micro-interactions: Live ticking countdown pills on mobile headers, amber warning states for the final 3 minutes, and pulsing rose alerts for the final 60-second sprint.

### 📊 5. Study Activity Heatmap & Analytics
* **12-Week Sunday-Aligned Heatmap**: GitHub-style activity rings tracking daily completions with active day inspection.
* **Animated Velocity Charts**: Interactive weekly output statistics and productivity breakdown.

### 📑 6. Print-Perfect Academic PDF & ICS/CSV Export
* **Isolated PDF Ledger Generator**: Clean print layout with university metadata headers, assignment checklists `[ ]`, and zero website chrome clutter.
* **Universal Calendar Export**: Export directly to `.ICS` (Google/Apple Calendar) and `.CSV`.

### 🔔 7. Automated Reminders & Celery Worker
* Asynchronous 24-hour deadline scanner and daily productivity digest engine.
* Automatic in-app notification center with real-time unread badges.

### 🔐 8. Dual-Role RBAC & System Administration
* **JWT Cryptographic Auth**: 15-minute access tokens + 7-day refresh tokens with PBKDF2 password hashing and rate limiting.
* **Admin User Directory**: Administrator portal to manage accounts, inspect workloads, and toggle account access with self-deletion safeguards.

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
│   ├── Dockerfile                  # Production container definition for Flask
│   ├── Procfile                    # Render / Railway process definitions
│   ├── .env.example                # Backend environment configuration template
│   ├── app/
│   │   ├── __init__.py             # Flask app factory, CORS init, admin auto-bootstrapper
│   │   ├── config.py               # Dynamic settings & database URL normalizer
│   │   ├── celery_app.py           # Celery beat schedules & task configuration
│   │   ├── commands.py             # CLI commands (flask seed, flask run-jobs)
│   │   ├── auth/                   # JWT registration, login, and token refresh
│   │   ├── projects/               # Course & syllabus management endpoints
│   │   ├── tasks/                  # Task ledger, Kanban, and subtask routes
│   │   ├── admin/                  # Admin user directory, block & delete routes
│   │   ├── analytics/              # Productivity metrics and report history
│   │   ├── notifications/          # In-app notifications & cron trigger endpoints
│   │   └── tasks_jobs/             # Asynchronous Celery reminder and digest tasks
│   └── tests/                      # Automated pytest API test suite
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
        ├── App.vue                 # Master shell (Desktop sidebar, mobile nav, user menu)
        ├── main.js                 # App initialization & Pinia store setup
        ├── style.css               # Design system, themes & print stylesheet
        ├── api/client.js           # Axios interceptors & auto-prefixing baseURL
        ├── components/             # Reusable UI components & modals
        ├── stores/                 # Pinia state stores (auth, tasks, timer, notifications)
        └── views/                  # Route views (Dashboard, Tasks, Calendar, Admin, etc.)
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

---

## 🔒 Security & Roles

TaskNova implements **Zero-Trust Role-Based Access Control (RBAC)**:

| Role | Creation | Permissions |
| :--- | :--- | :--- |
| `user` | Default on public registration (`/api/auth/register`) | Manage personal courses, task ledger, focus timer, and notifications. |
| `admin` | Auto-bootstrapped via `ADMIN_EMAIL` / `ADMIN_PASSWORD` env vars | All user capabilities + access to Admin Directory (`/admin`), account management, and system analytics. |

---

## 📡 API Reference Overview

| Method | Endpoint | Access | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register new student user |
| `POST` | `/api/auth/login` | Public | Sign in and obtain JWT access + refresh tokens |
| `POST` | `/api/auth/refresh` | Refresh Token | Refresh access token |
| `GET` | `/api/auth/me` | Authenticated | Fetch current profile |
| `GET/POST` | `/api/projects` | Authenticated | List or create courses |
| `GET/PUT/DELETE` | `/api/projects/:id` | Owner | Manage course details |
| `GET/POST` | `/api/tasks` | Authenticated | List with filters (status, priority, due date) or create task |
| `GET/PUT/DELETE` | `/api/tasks/:id` | Owner | Manage task |
| `POST` | `/api/tasks/:id/complete` | Owner | Quick complete task |
| `GET` | `/api/analytics/me` | Authenticated | Fetch heatmap, weekly velocity, and metrics |
| `GET` | `/api/notifications` | Authenticated | Fetch inbox notifications with unread counts |
| `GET/POST` | `/api/notifications/trigger-jobs` | Public/Cron | Execute reminder scan and daily reports |
| `GET/PATCH/DELETE` | `/api/admin/users` | Admin Only | User directory, block/unblock, and delete accounts |

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
* **Portfolio**: [vishalrathod.tech](https://portfolio-vishal-rathod.vercel.app)
* **License**: MIT
