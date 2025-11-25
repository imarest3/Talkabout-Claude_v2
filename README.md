# Talkabout

Sistema de gestión de actividades de conversación para MOOCs con videoconferencias programadas.

## Descripción

Talkabout es una aplicación web que permite crear actividades de conversación con convocatorias temporales para alumnos de MOOCs. La aplicación:

- Permite a profesores crear actividades y eventos temporales
- Los alumnos se inscriben a eventos específicos
- Envía recordatorios automáticos por correo
- Lanza videoconferencias automáticamente (Google Meet o JITSI)
- Divide participantes en grupos según configuración
- Registra estadísticas de inscripción y asistencia

## Stack Tecnológico

### Backend
- **Python 3.11**
- **Django 4.2** + Django REST Framework
- **Django Channels** (WebSockets para sala de espera en tiempo real)
- **Celery** (Tareas asíncronas y programadas)
- **PostgreSQL** (Base de datos)
- **Redis** (Broker de Celery + Cache + Backend de Channels)

### Frontend
- **React 18** con **TypeScript**
- **Material-UI (MUI)** (Componentes UI)
- **React Query** (Gestión de estado servidor)
- **React Router** (Enrutamiento)

### Infraestructura
- **Docker** + **Docker Compose**
- Contenedores separados: backend, frontend, db, redis, celery_worker, celery_beat

## Requisitos Previos

- Docker (>= 20.10)
- Docker Compose (>= 2.0)
- Git

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd Talkabout-Claude_v2
```

### 2. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y ajustar los valores:

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
POSTGRES_DB=talkabout_db
POSTGRES_USER=talkabout_user
POSTGRES_PASSWORD=your-secure-password

# Email (configurar para producción)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google Meet / Jitsi (opcional)
GOOGLE_CLIENT_ID=your-google-client-id
JITSI_DOMAIN=meet.jit.si
```

### 3. Construir y levantar los contenedores

```bash
docker-compose up --build
```

Esto levantará todos los servicios:
- **Backend Django**: http://localhost:8000
- **Frontend React**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Celery Worker**: Procesando tareas en segundo plano
- **Celery Beat**: Ejecutando tareas programadas

### 4. Aplicar migraciones de base de datos

En otra terminal, ejecutar:

```bash
docker-compose exec backend python manage.py migrate
```

### 5. Crear superusuario (administrador)

```bash
docker-compose exec backend python manage.py createsuperuser
```

Seguir las instrucciones para crear un usuario administrador.

### 6. Acceder a la aplicación

- **Frontend**: http://localhost:3000
- **Admin Django**: http://localhost:8000/admin
- **API REST**: http://localhost:8000/api/

## Estructura del Proyecto

```
Talkabout-Claude_v2/
├── backend/
│   ├── apps/
│   │   ├── users/          # Gestión de usuarios
│   │   ├── activities/     # Actividades y archivos
│   │   ├── events/         # Eventos e inscripciones
│   │   └── meetings/       # Reuniones y participantes
│   ├── talkabout/
│   │   ├── settings.py     # Configuración Django
│   │   ├── urls.py         # URLs principales
│   │   ├── celery.py       # Configuración Celery
│   │   └── asgi.py         # Configuración ASGI (Channels)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Componente principal
│   │   └── index.tsx       # Punto de entrada
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
├── .env.example
├── .gitignore
├── DATABASE_SCHEMA.md      # Documentación del esquema de BD
└── README.md
```

## Modelos de Base de Datos

### User
- Usuarios del sistema (Admin, Profesor, Estudiante)
- Código único (generado o de edX)
- Email y zona horaria
- Soporte para anonimización (GDPR)

### Activity
- Actividad de conversación
- Descripción HTML y archivos adjuntos
- Máximo de participantes por reunión

### Event
- Convocatoria temporal de una actividad
- Configuración de recordatorios
- Estados: scheduled → in_waiting → in_progress → completed

### Enrollment
- Inscripción de usuario a evento
- Token de desinscripción
- Estados: enrolled, cancelled, attended, no_show

### Meeting
- Videoconferencia generada (Google Meet o JITSI)
- URL y ID del meeting
- Participantes asignados

### MeetingParticipant
- Tracking de asistencia real
- Estados: waiting → joined → left

Ver `DATABASE_SCHEMA.md` para detalles completos.

## Comandos Útiles

### Backend (Django)

```bash
# Acceder al shell de Django
docker-compose exec backend python manage.py shell

# Crear migraciones
docker-compose exec backend python manage.py makemigrations

# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser

# Ver logs
docker-compose logs -f backend
```

### Frontend (React)

```bash
# Instalar dependencias (si se modifica package.json)
docker-compose exec frontend npm install

# Ver logs
docker-compose logs -f frontend
```

### Celery

```bash
# Ver logs del worker
docker-compose logs -f celery_worker

# Ver logs del beat
docker-compose logs -f celery_beat

# Reiniciar worker
docker-compose restart celery_worker
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U talkabout_user -d talkabout_db

# Hacer backup
docker-compose exec db pg_dump -U talkabout_user talkabout_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U talkabout_user talkabout_db < backup.sql
```

### Detener servicios

```bash
# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: borra la BD)
docker-compose down -v
```

## Desarrollo

### Agregar nuevas dependencias

**Backend (Python):**
1. Agregar en `backend/requirements.txt`
2. Reconstruir: `docker-compose up --build backend`

**Frontend (Node):**
1. Agregar en `frontend/package.json`
2. Reconstruir: `docker-compose up --build frontend`

### Ejecutar tests

```bash
# Backend
docker-compose exec backend python manage.py test

# Frontend (cuando se implementen)
docker-compose exec frontend npm test
```

## Documentación de API

La documentación completa de la API REST está disponible en [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md).

### Endpoints Disponibles

**Autenticación (Fase 2):**
- `POST /api/users/auth/register/` - Registro normal
- `POST /api/users/auth/register/edx/` - Registro desde edX
- `POST /api/users/auth/login/` - Login
- `POST /api/users/auth/logout/` - Logout
- `POST /api/users/auth/token/refresh/` - Refresh token

**Perfil de Usuario (Fase 2):**
- `GET /api/users/profile/` - Ver perfil
- `PUT/PATCH /api/users/profile/update/` - Actualizar perfil
- `POST /api/users/profile/change-password/` - Cambiar contraseña
- `POST /api/users/profile/anonymize/` - Anonimizar usuario

**Actividades (Fase 3):**
- `GET /api/activities/` - Listar actividades (con filtros y búsqueda)
- `POST /api/activities/create/` - Crear actividad
- `GET /api/activities/<code>/` - Ver detalle de actividad
- `PUT/PATCH /api/activities/<code>/update/` - Actualizar actividad
- `DELETE /api/activities/<code>/delete/` - Eliminar actividad
- `POST /api/activities/<code>/files/upload/` - Subir archivo
- `DELETE /api/activities/<code>/files/<file_id>/delete/` - Eliminar archivo
- `GET /api/activities/<code>/statistics/` - Estadísticas de actividad

**Eventos (Fase 4):**
- `GET /api/events/` - Listar eventos (con filtros)
- `POST /api/events/create/` - Crear evento individual
- `POST /api/events/bulk-create/` - Crear eventos masivamente
- `GET /api/events/<id>/` - Ver detalle de evento
- `PUT/PATCH /api/events/<id>/update/` - Actualizar evento
- `DELETE /api/events/<id>/delete/` - Eliminar evento
- `POST /api/events/enroll/` - Inscribirse a evento
- `POST /api/events/<id>/unenroll/` - Desinscribirse de evento
- `GET /api/events/my-enrollments/` - Ver mis inscripciones
- `GET /api/events/<id>/enrollments/` - Ver inscripciones del evento (teacher/admin)
- `POST /api/events/convert-timezone/` - Convertir zonas horarias
- `GET /api/events/<id>/statistics/` - Estadísticas del evento

Ver [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) para ejemplos de uso, request/response formats, y códigos de error.

## Plan de Desarrollo Incremental

### ✅ Fase 1: Fundamentos (COMPLETADA)
- Estructura de proyecto
- Docker Compose
- Modelos de base de datos
- Configuración Django + React

### ✅ Fase 2: Sistema de Autenticación (COMPLETADA)
- Serializers para User (registro, login, perfil)
- Registro normal (genera user_code único)
- Registro desde edX (usa USER_ID con hash SHA-1)
- Login con JWT (access + refresh tokens)
- Logout con blacklist de tokens
- Ver y actualizar perfil de usuario
- Cambiar contraseña
- Anonimización de usuarios (GDPR)
- Sistema de permisos por roles (Admin, Profesor, Estudiante)
- Tests de autenticación
- Documentación completa de API (ver `API_DOCUMENTATION.md`)

### ✅ Fase 3: CRUD de Actividades (COMPLETADA)
- Serializers para Activity y ActivityFile
- CRUD completo de actividades (crear, listar, ver, actualizar, eliminar)
- Subir y eliminar archivos adjuntos (max 10MB)
- Filtros y búsqueda de actividades
- Permisos por roles (solo profesores/admins pueden crear/editar)
- Soft delete de actividades con eventos
- Estadísticas de actividades (eventos, inscripciones, asistencia)
- Tests completos
- Documentación de API actualizada

### ✅ Fase 4: Gestión de Eventos (COMPLETADA)
- Serializers para Event y Enrollment
- CRUD completo de eventos (crear, listar, ver, actualizar, eliminar)
- Creación masiva de eventos (rango fechas + horas UTC)
- Inscripción y desinscripción de usuarios a eventos
- Ver mis inscripciones
- Ver inscripciones de un evento (solo teachers/admins)
- Conversión de zonas horarias (UTC ↔ timezone local)
- Estadísticas de eventos (inscritos, asistentes, cancelados)
- Validaciones (eventos futuros, no editar pasados, etc.)
- Tests completos
- Documentación de API actualizada

### Fase 5: Sistema de Notificaciones y Emails
- Emails de confirmación de inscripción
- Recordatorios programados
- Email de sala de espera
- Manejo de respuestas (aceptar/rechazar)
- Enlaces de desinscripción

### Fase 6-13: Ver plan completo en documentación

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

[Especificar licencia]

## Contacto

[Información de contacto]
