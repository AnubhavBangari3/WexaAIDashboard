# Wexa AI Dashboard  
### Real-Time Analytics & Reporting Platform

A production-style SaaS analytics platform built using **Django REST Framework**, **Next.js**, **Redis**, **Celery**, and **WebSockets**.  
The platform enables organizations to ingest events from multiple sources, visualize metrics through dashboards, configure alerts, generate reports, and receive real-time updates.

---

# Live Demo

## Frontend
https://wexa-aidash-frontend-ab2.vercel.app

## Backend API
https://wexaaidashboard-1.onrender.com

---

# Project Architecture

```txt
                    ┌──────────────────────┐
                    │   Next.js Frontend   │
                    │  (Vercel Deployment) │
                    └──────────┬───────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Django REST API Backend  │
                 │   DRF + Django Channels  │
                 └──────────┬───────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
   SQLite Database        Redis            Celery Workers
      Event Storage    Cache + Broker     Async Processing
                                                │
                                                ▼
                                   Scheduled Tasks / Alerts
```

---

# Core Features

## Authentication & Multi-Tenancy

- JWT Authentication
- Refresh Tokens
- Role-Based Access
  - Owner
  - Admin
  - Analyst
  - Viewer
- Organization-based Data Isolation
- Invite-based Team Management

---

## Data Ingestion

- Single Event API
- Batch Event API
- CSV Upload Processing
- Webhook Receiver API
- Schema Validation
- API Key Authentication
- Redis-backed Rate Limiting
- Async Event Processing using Celery

---

## Dashboards & Visualizations

- Dashboard CRUD
- Widget CRUD
- KPI Cards
- Line Charts
- Bar Charts
- Pie Charts
- Saved Queries
- Time Filters
- Auto Refresh
- Fullscreen Dashboard Mode
- Dashboard Templates
- Dashboard Sharing

---

## Alerts & Notifications

- Threshold-Based Alerts
- Celery Beat Scheduling
- Real-Time Alert Broadcasting
- Email Notifications
- Webhook Notifications
- Alert History
- Mute / Snooze Alerts
- Alert Status Tracking

---

## Scheduled Reports

- Scheduled Dashboard Reports
- PDF Report Generation
- PNG Dashboard Snapshots
- Email Delivery
- Report History
- Report Downloads

---

## Real-Time Features

- Django Channels WebSockets
- Live Dashboard Refresh
- Live Event Stream Viewer
- Real-Time Notifications
- Automatic Reconnection
- Organization-Level Isolation

---

# Tech Stack

## Frontend

| Technology | Usage |
|---|---|
| Next.js 16 | Frontend Framework |
| TypeScript | Type Safety |
| Tailwind CSS | Styling |
| React Query | API State Management |
| Recharts | Charts |
| Axios | API Communication |
| React Hook Form | Forms |
| Lucide React | Icons |

---

## Backend

| Technology | Usage |
|---|---|
| Django | Backend Framework |
| Django REST Framework | REST APIs |
| Django Channels | WebSockets |
| Celery | Background Tasks |
| Redis | Cache + Broker |
| SimpleJWT | Authentication |
| Pydantic | Validation |
| Pandas | CSV Processing |

---

# Folder Structure

```txt
WexaAIDashboard/
│
├── frontend/                  # Next.js frontend
│
├── backend/                   # Django settings/config
│
├── accounts/                  # Authentication & roles
├── organizations/             # Multi-tenancy
├── ingestion/                 # Event ingestion system
├── dashboards/                # Dashboards & widgets
├── alerts/                    # Alerts & notifications
├── reports/                   # Scheduled reports
│
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Backend Setup

## Clone Repository

```bash
git clone https://github.com/AnubhavBangari3/WexaAIDashboard.git
cd WexaAIDashboard
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv env
env\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv env
source env/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create `.env`

```env
SECRET_KEY=your_secret_key
DEBUG=True

ALLOWED_HOSTS=*

REDIS_URL=redis://127.0.0.1:6379

CELERY_BROKER_URL=redis://127.0.0.1:6379
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379
```

---

# Run Backend

## Start Redis

# Run Backend

## Start Redis (Docker)

```bash
docker run --name redis-wexa -p 6379:6379 redis
```

---

## Start Django Server

```bash
python manage.py runserver
```

---

## Start Celery Worker

### Windows

```bash
celery -A backend worker -l info --pool=solo
```

### Linux / Mac

```bash
celery -A backend worker -l info
```

---

## Start Celery Beat Scheduler

```bash
celery -A backend beat -l info
```

---

# Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

# Frontend Environment Variable

Create:

```txt
frontend/.env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=https://wexaaidashboard-1.onrender.com
```

---

# API Overview

## Authentication APIs

```txt
/api/auth/signup/
/api/auth/login/
/api/auth/refresh/
/api/auth/invite/
```

---

## Ingestion APIs

```txt
/api/ingestion/events/
/api/ingestion/events/batch/
/api/ingestion/csv/
/api/ingestion/webhook/
```

---

## Dashboard APIs

```txt
/api/dashboards/
/api/widgets/
```

---

## Alerts APIs

```txt
/api/alerts/
/api/alerts/rules/
/api/alerts/history/
```

---

## Reports APIs

```txt
/api/reports/
/api/reports/history/
```

---

# WebSocket Support

## Real-Time Event Stream

```txt
ws://localhost:8000/ws/events/
```

---

## Real-Time Alerts

```txt
ws://localhost:8000/ws/alerts/
```

---

# Testing

Run tests:

```bash
python manage.py test
```

Covered Areas:

- Event Creation
- Batch Event Processing
- API Key Validation
- Organization Isolation
- Authentication Validation

---

# Security Features

- JWT Authentication
- Role-Based Permissions
- Organization Isolation
- Redis Rate Limiting
- Serializer Validation
- ORM-based Query Protection
- CORS Configuration

---

# Architecture Design

The project follows a layered architecture:

```txt
Views → Services → Models
```

## Separation of Concerns

| Layer | Responsibility |
|---|---|
| Views | API layer |
| Services | Business logic |
| Models | Database layer |
| Tasks | Async processing |
| Consumers | WebSocket handling |

---

# Deployment

## Frontend Deployment

- Vercel

## Backend Deployment

- Render

## Redis

- Render Key Value

---

# Future Improvements

- PostgreSQL Production Database
- OpenTelemetry Integration
- Distributed Tracing
- Feature Flags
- CI/CD Pipeline
- Load Testing
- GraphQL APIs

---

# Assessment Coverage

| Module | Status |
|---|---|
| Authentication & Multi-Tenancy | ✅ Completed |
| Data Ingestion & Sources | ✅ Completed |
| Dashboards & Visualizations | ✅ Completed |
| Alerts & Notifications | ✅ Completed |
| Scheduled Reports | ✅ Completed |
| Real-Time Features | ✅ Completed |

---

# Author

## Anubhav Bangari

- Python Developer
- Full Stack Developer
- AI & Real-Time Systems Enthusiast

GitHub:
https://github.com/AnubhavBangari3