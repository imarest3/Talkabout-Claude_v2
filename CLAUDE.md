# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Talkabout is a Django + React platform for managing conversational activities and video conference events, built for MOOCs at Universidad Politécnica de Valencia (UPV). It supports role-based access (admin/teacher/student), JWT auth, async task scheduling, WebSocket real-time communication, and Jitsi video conference integration.

## Common Commands

All services run via Docker Compose. There is no local dev setup outside containers.

```bash
# Start all services (backend :8000, frontend :3000)
docker-compose up --build

# Apply migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run backend tests
docker-compose exec backend python manage.py test

# Run a specific test app
docker-compose exec backend python manage.py test apps.events

# Django shell
docker-compose exec backend python manage.py shell

# Make migrations after model changes
docker-compose exec backend python manage.py makemigrations

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

Frontend (inside container or locally with Node):
```bash
cd frontend
npm start        # Dev server
npm run build    # Production build
npm test         # Tests
```

## Architecture

### Services (docker-compose.yml)
- **db** – PostgreSQL 15
- **redis** – Redis 7 (Celery broker + Django Channels layer)
- **backend** – Django 4.2 + DRF + Daphne (ASGI)
- **celery_worker** – Async task execution
- **celery_beat** – Scheduled tasks (reminders, meeting creation, cleanup)
- **frontend** – React 18 dev server

### Backend (`backend/`)

Django project `talkabout` with four apps:

| App | Responsibility |
|-----|----------------|
| `apps/users` | Custom User model (uuid PK, role, timezone), JWT auth, profile |
| `apps/activities` | Activity + ActivityFile CRUD (teacher/admin only), campo `max_participants` |
| `apps/events` | Event lifecycle, Enrollment, email notifications |
| `apps/meetings` | Jitsi Meeting + MeetingParticipant, participant distribution |

Key files:
- `talkabout/settings.py` – All configuration (DB falls back to SQLite if `POSTGRES_DB` is unset)
- `talkabout/celery.py` – Beat schedule (runs every 1–10 min: reminders, meeting creation, cleanup)
- `talkabout/asgi.py` – WebSocket routing for waiting room
- `apps/events/tasks.py` – All Celery tasks

**Event state machine:** `scheduled → in_waiting → in_progress → completed`

### Frontend (`frontend/src/`)

React 18 + TypeScript SPA:

- `App.tsx` – Router with `PrivateRoute` protection
- `context/AuthContext.tsx` – JWT state (localStorage), auto-refresh on 401
- `services/api/client.ts` – Axios instance with token interceptors
- `pages/` – Activities list/detail/form, Events create/detail/waiting-room, Profile, Calendar
- `pages/calendar/CalendarPage.tsx` – Vista de calendario con todos los eventos del usuario
- `components/layout/MainLayout.tsx` – Shell wrapping all pages
- `components/layout/Navbar.tsx` – Navegación principal (incluye enlace al calendario)
- `types/index.ts` – Shared TypeScript interfaces for all domain entities

State management uses **React Query** (v5) for server state; no Redux/Zustand.

### Authentication

JWT via SimpleJWT: 60-min access tokens, 7-day rotatable refresh tokens with blacklist on logout. Two registration paths:
- Normal: email + password → auto-generated `user_code`
- edX: SHA-1 hashed edX user ID as `user_code`

### Async / Real-time

- **Celery Beat** periodically sends reminder emails, triggers waiting-room notifications, creates Jitsi meetings, and cleans up past events
- **Django Channels** (Redis channel layer) powers the WebSocket waiting room; frontend hook: `useWaitingRoom.ts`

## Environment Variables

Copy `.env.example` to `.env`. Minimal required variables:

```
# Database
POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

# Email
EMAIL_BACKEND, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

# Frontend
REACT_APP_API_URL=http://localhost:8000/api
FRONTEND_URL=http://localhost:3000
```

Django `SECRET_KEY` is auto-generated in dev if not set.

## Recent Changes (branch: version-mejorada)

- **Activity.max_participants** – Nuevo campo en el modelo Activity con migración `0004_activity_max_participants.py`
- **Serializers actualizados** – `activities` y `events` con soporte para los nuevos campos
- **EventFormPage mejorado** – Más opciones de configuración y validaciones en el formulario de eventos
- **CalendarPage** – Nueva página `frontend/src/pages/calendar/CalendarPage.tsx` con vista de calendario de eventos
- **Navbar** – Enlace al calendario añadido en la navegación principal
- **WaitingRoomPage / ActivityDetailPage / ActivityFormPage** – Ajustes y mejoras de UX

## Documentation

Extended docs in `docs/`:
- `API_DOCUMENTATION.md` – Full REST API reference
- `DATABASE_SCHEMA.md` – Model field details and relationships
- `ESTADO_PROYECTO.md` – Frontend architecture and completion status
- `POSTMAN_GUIDE.md` – API testing guide
