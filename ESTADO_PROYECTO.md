# Estado Actual del Proyecto: Talkabout UPV (Frontend)

Este documento sirve como referencia rápida para consultoría sobre el estado del frontend de Talkabout UPV, su arquitectura y los endpoints que consume.

## Contexto del Proyecto

**Talkabout UPV** es una plataforma de apoyo y práctica conversacional en línea diseñada para estudiantes de idiomas y miembros de la Universitat Politècnica de València (UPV). A través de la plataforma, los profesores y administradores pueden crear "Actividades" conversacionales, dentro de las cuales se programan "Eventos". Los alumnos se inscriben a dichos eventos y, al llegar la hora estipulada, acceden a una sala de espera. En base a los aforos, el sistema realiza automáticamente el emparejamiento de los estudiantes en pequeños grupos y genera salas de videollamada, enviando el enlace en tiempo real y gestionando a los participantes.

La infraestructura del sistema se basa en un entorno de contenedores gestionado por **Docker**.
- El **Frontend** es una Single Page Application (SPA) en React sirviendo interfaces interactivas.
- El **Backend** está construido en Python (Django + Django REST Framework) junto con Django Channels para la gestión de WebSockets (para las salas de espera).
- Para el fondo asíncrono y los emparejamientos orquestados, el ecosistema se apoya en **PostgreSQL** para persistencia, **Redis** como bróker temporal e in-memory db, y **Celery** (junto con Celery Beat) para tareas en segundo plano.

---

## Estructura de Carpetas (`frontend/src/`)

```
src/
├── App.tsx                      # Punto de entrada de componentes. Configura React Router, temas y Providers de la app.
├── assets/                       # Contiene recursos estáticos visuales (como `upv-logo.png`).
├── components/                   # Componentes visuales genéricos y de enrutamiento.
│   ├── auth/PrivateRoute.tsx     # Higher-Order Component para proteger rutas que exigen autenticación.
│   └── layout/                   # Envoltorios de la interfaz principal.
│       ├── Footer.tsx            # Pie de página.
│       ├── MainLayout.tsx        # Contenedor padre general con diseño por defecto.
│       └── Navbar.tsx            # Barra de navegación principal del sistema.
├── context/
│   └── AuthContext.tsx           # Context global para control de sesión en localStorage, refresh y data de usuario.
├── hooks/
│   └── useWaitingRoom.ts         # Custom Hook que levanta y gestiona la sesión de WebSockets en el evento de espera.
├── index.tsx                     # Punto de montaje de la aplicación React.
├── pages/                        # Componentes principales correspondientes a cada página.
│   ├── activities/
│   │   ├── ActivityDetailPage.tsx# Vista detalle de actividad, sus eventos listados y archivos subidos.
│   │   ├── ActivityFormPage.tsx  # Formulario enriquecido para la creación y edición de actividades.
│   │   └── ActivityListPage.tsx  # Catálogo general con buscador para apuntarse a actividades.
│   ├── auth/
│   │   └── LoginPage.tsx         # Pantalla de inicio de sesión de usuario y redirección natural.
│   ├── events/
│   │   ├── EventFormPage.tsx     # Creador de un evento temporal dentro de una actividad, definiendo recordatorios.
│   │   └── WaitingRoomPage.tsx   # Sala de espera del evento; orquesta conteo y redirección a videollamadas.
│   └── profile/
│       └── ProfilePage.tsx       # Perfil del participante para modificar horarios locales, email y contraseñas.
├── services/api/
│   └── client.ts                 # Configuración del axios con un cliente base y los interceptores de token.
├── theme/
│   └── index.ts                  # Declaración base visual centralizada de las guías de diseño en Material UI.
└── types/
    ├── index.ts                  # Contratos e interfaces base en TypeScript para tipar datos REST.
    └── react-quill.d.ts          # Declaración manual de soporte modular en TypeScript para react-quill-new.
```

---

## Decisiones Técnicas Adoptadas

- **React (18.2.0) y TypeScript**: Aseguran una tipificación estricta del negocio en la interfaz, lo cual previene bugs de manera pasiva y documenta naturalmente el código.
- **Material UI (@mui/material v5) y Emotion**: Adoptados por la agilidad en la construcción de layouts corporativos prefabricados y consistentes, minimizando el tiempo de escritura de CSS puro.
- **React Query (@tanstack/react-query v5)**: Encargado de las llamadas al backend, caché y sincronización asíncrona en toda la plataforma. Simplifica infinitamente el control de estados "loading" y "error".
- **React Router DOM (v6)**: Implementado para orquestar la navegación de interfaz cliente, la redirección anidada y el rechazo en caso de rutas privadas (AuthContext).
- **React Quill New**: Un reemplazo moderno del react-quill abandonado. Se adoptó para solucionar errores de deprecación en la gestión estricta del DOM de React (`findDOMNode` bugs).
- **Date-fns y Date-fns-tz**: Facilitan el formateo idiomático y manipulación de fechas en pantalla considerando la zona horaria dinámica elegida por cada usuario.

---

## Estado de las Páginas Principales

1. **ActivityListPage**: Implementada. Lista y busca entidades con feedback de esqueleto (Skeleton cards).
    - *Pendiente / Limitaciones:* No gestiona la paginación a pesar de que la API soporta `next`/`previous/count`. Carece de "debounce" real en la barra de búsqueda de red, recargando ante cada tipeo.
2. **ActivityDetailPage**: Implementada y robusta. Combina listas filtradas de eventos próximos y pasados, soporta borrado de su entidad y permite la carga o manejo de archivos adjuntos.
    - *Pendiente / Limitaciones:* En móvil, la división de columnas para los eventos se apila al final, pero requiere mejora del espacio.
3. **ActivityFormPage** / **EventFormPage**: Ambos cubiertos. El primero usa Quill, el segundo pickers de fecha MUI. Validaciones completas implementadas con Snackbar (Alerts).
4. **WaitingRoomPage**: Sumamente compleja y en óptimo estado actual. Empalma la vista a tiempo real del WS usando un Hook a medida. Maneja estado "Iniciado", "Terminado", "Descubriendo Sala" y permite la redirección directa por window target abierto.
5. **ProfilePage**: Maneja tres formularios segregados (Datos, Configuración nativa `Intl` de husos horarios y Contraseña particular). Completamente útil.
6. **LoginPage**: Normal y estandarizada, permite auto-continuación a la ruta que intentó acceder antes del login (State "From").
7. **Ruta "Registro" (`/register`)**: Tiene solo un `Placeholder`. *Deuda principal técnica (No codificada).*

---

## Integración con Endpoints REST

La plataforma cuenta con un cliente API base configurado con intercepción del token (tanto de inyección como de repetición tras refresco).

*Endpoints de usuarios / sesión:*
- `POST /users/auth/login/`
- `POST /users/auth/logout/`
- `POST /users/auth/token/refresh/`
- `GET /users/profile/`
- `PATCH /users/profile/update/`
- `POST /users/profile/change-password/`

*Endpoints de Actividades (Activities):*
- `GET /activities/` (Soporta query arg `search`)
- `GET /activities/:code/`
- `POST /activities/create/`
- `PATCH /activities/:code/update/`
- `DELETE /activities/:code/delete/`
- `POST /activities/:code/files/upload/` (Form-data subida)
- `DELETE /activities/:code/files/:fileId/delete/`

*Endpoints de Eventos e Inscripción:*
- `GET /events/` (Con params de `activity_code`)
- `POST /events/` (Generación desde form)
- `GET /events/:eventId/` (Consulta directa base para la sala de espera)
- `GET /events/my-enrollments/`
- `POST /events/enroll/` 
- `POST /events/:eventId/unenroll/`
- `GET /events/:eventId/my-meeting/` (Se encarga de recuperar la URL exclusiva de Jitsi del estudiante)

*(La conexión en tiempo real se lleva a cabo enviando un Upgrade desde un endpoint asíncrono hacia Websockets de Django Channels para la emisión activa por el canal).*
