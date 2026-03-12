# 📮 Guía Completa de Pruebas con Postman - Talkabout API

## 🎯 Objetivo
Esta guía te permitirá probar todos los endpoints de la API de Talkabout usando Postman paso a paso.

---

## 📋 Requisitos Previos

1. **Postman instalado** (descarga desde https://www.postman.com/downloads/)
2. **Docker containers corriendo** (ejecuta `docker-compose up` si no están activos)
3. **Servidor backend activo** en `http://localhost:8000`

---

## 🚀 PASO 1: Configurar Postman

### 1.1 Crear una Nueva Colección

1. Abre Postman
2. Click en **"Collections"** en el panel izquierdo
3. Click en **"+"** o **"Create Collection"**
4. Nombra la colección: **"Talkabout API"**

### 1.2 Crear Variables de Entorno

1. Click en **"Environments"** (icono de ojo en la esquina superior derecha)
2. Click en **"+"** para crear un nuevo entorno
3. Nómbralo: **"Talkabout Local"**
4. Añade las siguientes variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://localhost:8000/api` | `http://localhost:8000/api` |
| `access_token` | (dejar vacío) | (dejar vacío) |
| `refresh_token` | (dejar vacío) | (dejar vacío) |
| `teacher_code` | `user_f68ff4c7193a` | `user_f68ff4c7193a` |
| `student_code` | `user_330363762e81` | `user_330363762e81` |

5. Click en **"Save"**
6. Selecciona el entorno **"Talkabout Local"** en el dropdown superior derecho

---

## 🔐 PASO 2: Autenticación

### 2.1 Login como Teacher

**Crear la petición:**

1. En la colección "Talkabout API", click en **"Add request"**
2. Nombre: **"Login - Teacher"**
3. Método: **POST**
4. URL: `{{base_url}}/users/auth/login/`

**Configurar Headers:**

1. Click en la pestaña **"Headers"**
2. Añade:
   - Key: `Content-Type`
   - Value: `application/json`

**Configurar Body:**

1. Click en la pestaña **"Body"**
2. Selecciona **"raw"**
3. Selecciona **"JSON"** en el dropdown
4. Pega este JSON:

```json
{
  "user_code": "{{teacher_code}}",
  "password": "Teacher123!"
}
```

**Configurar Tests (para guardar tokens automáticamente):**

1. Click en la pestaña **"Tests"**
2. Pega este código:

```javascript
// Guardar tokens en variables de entorno
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
    console.log("✓ Tokens guardados correctamente");
    console.log("Access Token:", jsonData.access);
}
```

**Ejecutar:**

1. Click en **"Send"**
2. Deberías ver una respuesta **200 OK** con:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "...",
    "user_code": "user_f68ff4c7193a",
    "email": "teacher_test@talkabout.com",
    "role": "teacher",
    "timezone": "Europe/Madrid"
  }
}
```

3. Los tokens se guardarán automáticamente en las variables de entorno

---

### 2.2 Login como Student

**Crear la petición:**

1. Duplica la petición anterior (click derecho → Duplicate)
2. Renombra a: **"Login - Student"**
3. Cambia el body a:

```json
{
  "user_code": "{{student_code}}",
  "password": "Student123!"
}
```

4. Click en **"Send"**
5. Deberías ver la respuesta con `"role": "student"`

---

### 2.3 Registro de Nuevo Usuario

**Crear la petición:**

1. Add request → Nombre: **"Register - New User"**
2. Método: **POST**
3. URL: `{{base_url}}/users/auth/register/`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):

```json
{
  "email": "nuevo_usuario@test.com",
  "password": "MiPassword123!",
  "password_confirm": "MiPassword123!",
  "timezone": "America/Mexico_City"
}
```

6. Click en **"Send"**
7. Respuesta esperada: **201 Created** con tokens y datos del usuario

---

## 👤 PASO 3: Perfil de Usuario

### 3.1 Ver Mi Perfil

**Crear la petición:**

1. Add request → Nombre: **"Get My Profile"**
2. Método: **GET**
3. URL: `{{base_url}}/users/profile/`

**Configurar Autorización:**

1. Click en la pestaña **"Authorization"**
2. Type: **"Bearer Token"**
3. Token: `{{access_token}}`

4. Click en **"Send"**
5. Respuesta esperada: **200 OK** con tus datos de usuario

---

### 3.2 Actualizar Perfil

**Crear la petición:**

1. Add request → Nombre: **"Update Profile"**
2. Método: **PATCH**
3. URL: `{{base_url}}/users/profile/update/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "timezone": "Europe/London"
}
```

7. Click en **"Send"**

---

### 3.3 Cambiar Contraseña

**Crear la petición:**

1. Add request → Nombre: **"Change Password"**
2. Método: **POST**
3. URL: `{{base_url}}/users/change-password/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "old_password": "Teacher123!",
  "new_password": "NuevaPassword123!",
  "new_password_confirm": "NuevaPassword123!"
}
```

7. Click en **"Send"**

---

## 📚 PASO 4: Actividades

### 4.1 Listar Actividades

**Crear la petición:**

1. Add request → Nombre: **"List Activities"**
2. Método: **GET**
3. URL: `{{base_url}}/activities/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Click en **"Send"**

**Respuesta esperada:**

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "...",
      "code": "TEST001",
      "title": "Test Activity",
      "description": "<p>Test</p>",
      "max_participants_per_meeting": 6,
      "is_active": true,
      "created_by": {...},
      "files": []
    }
  ]
}
```

---

### 4.2 Crear Actividad (como Teacher)

**IMPORTANTE:** Asegúrate de estar logueado como teacher (ejecuta "Login - Teacher" primero)

**Crear la petición:**

1. Add request → Nombre: **"Create Activity"**
2. Método: **POST**
3. URL: `{{base_url}}/activities/create/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "code": "ENG001",
  "title": "English Conversation Practice",
  "description": "<p>Practice your English speaking skills in small groups</p>",
  "max_participants_per_meeting": 6,
  "is_active": true
}
```

7. Click en **"Send"**
8. Respuesta esperada: **201 Created**

---

### 4.3 Ver Detalle de Actividad

**Crear la petición:**

1. Add request → Nombre: **"Get Activity Detail"**
2. Método: **GET**
3. URL: `{{base_url}}/activities/ENG001/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Click en **"Send"**

---

### 4.4 Actualizar Actividad

**Crear la petición:**

1. Add request → Nombre: **"Update Activity"**
2. Método: **PATCH**
3. URL: `{{base_url}}/activities/ENG001/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "title": "English Conversation - Advanced",
  "max_participants_per_meeting": 8
}
```

7. Click en **"Send"**

---

### 4.5 Subir Archivo a Actividad

**Crear la petición:**

1. Add request → Nombre: **"Upload File to Activity"**
2. Método: **POST**
3. URL: `{{base_url}}/activities/ENG001/upload-file/`
4. Authorization: **Bearer Token** → `{{access_token}}`

**Configurar Body:**

1. Click en la pestaña **"Body"**
2. Selecciona **"form-data"**
3. Añade:
   - Key: `file` (cambia el tipo a **"File"** en el dropdown)
   - Value: Click en **"Select Files"** y elige un archivo PDF o imagen
   - Key: `description`
   - Value: `Material de apoyo para la clase`

4. Click en **"Send"**
5. Respuesta esperada: **201 Created** con los datos del archivo

---

### 4.6 Estadísticas de Actividad

**Crear la petición:**

1. Add request → Nombre: **"Activity Statistics"**
2. Método: **GET**
3. URL: `{{base_url}}/activities/ENG001/statistics/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Click en **"Send"**

---

## 📅 PASO 5: Eventos

### 5.1 Listar Eventos

**Crear la petición:**

1. Add request → Nombre: **"List Events"**
2. Método: **GET**
3. URL: `{{base_url}}/events/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Click en **"Send"**

---

### 5.2 Crear Evento Individual

**Crear la petición:**

1. Add request → Nombre: **"Create Single Event"**
2. Método: **POST**
3. URL: `{{base_url}}/events/create/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "activity_code": "ENG001",
  "start_datetime": "2026-01-28T10:00:00Z",
  "end_datetime": "2026-01-28T11:00:00Z",
  "waiting_time_minutes": 10,
  "first_reminder_minutes": 1440,
  "second_reminder_minutes": 60
}
```

**NOTA:** Ajusta las fechas a fechas futuras (mañana o pasado mañana)

7. Click en **"Send"**
8. Respuesta esperada: **201 Created**

---

### 5.3 Crear Eventos Masivos

**Crear la petición:**

1. Add request → Nombre: **"Bulk Create Events"**
2. Método: **POST**
3. URL: `{{base_url}}/events/bulk-create/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "activity_code": "ENG001",
  "start_date": "2026-01-28",
  "end_date": "2026-02-03",
  "hours_utc": ["09:00", "14:00", "18:00"],
  "duration_minutes": 60,
  "waiting_time_minutes": 10,
  "first_reminder_minutes": 1440,
  "second_reminder_minutes": 60
}
```

7. Click en **"Send"**
8. Respuesta esperada: **201 Created** con mensaje de cuántos eventos se crearon

---

### 5.4 Inscribirse a un Evento (como Student)

**IMPORTANTE:** Primero ejecuta "Login - Student" para obtener el token de estudiante

**Obtener ID de un evento:**

1. Ejecuta "List Events"
2. Copia el `id` de uno de los eventos de la respuesta

**Crear la petición:**

1. Add request → Nombre: **"Enroll to Event"**
2. Método: **POST**
3. URL: `{{base_url}}/events/enroll/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "event_id": "PEGA_AQUI_EL_ID_DEL_EVENTO"
}
```

7. Click en **"Send"**
8. Respuesta esperada: **201 Created**

---

### 5.5 Ver Mis Inscripciones

**Crear la petición:**

1. Add request → Nombre: **"My Enrollments"**
2. Método: **GET**
3. URL: `{{base_url}}/events/my-enrollments/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Click en **"Send"**

---

### 5.6 Desinscribirse de un Evento

**Crear la petición:**

1. Add request → Nombre: **"Unenroll from Event"**
2. Método: **POST**
3. URL: `{{base_url}}/events/unenroll/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "event_id": "ID_DEL_EVENTO"
}
```

7. Click en **"Send"**

---

### 5.7 Ver Inscripciones de un Evento (como Teacher)

**IMPORTANTE:** Ejecuta "Login - Teacher" primero

**Crear la petición:**

1. Add request → Nombre: **"Event Enrollments"**
2. Método: **GET**
3. URL: `{{base_url}}/events/ID_DEL_EVENTO/enrollments/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Click en **"Send"**

---

## 🔄 PASO 6: Refresh Token

### 6.1 Refrescar Access Token

**Crear la petición:**

1. Add request → Nombre: **"Refresh Token"**
2. Método: **POST**
3. URL: `{{base_url}}/users/auth/token/refresh/`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):

```json
{
  "refresh": "{{refresh_token}}"
}
```

**Configurar Tests:**

```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
    console.log("✓ Tokens actualizados");
}
```

6. Click en **"Send"**

---

## 🚪 PASO 7: Logout

### 7.1 Cerrar Sesión

**Crear la petición:**

1. Add request → Nombre: **"Logout"**
2. Método: **POST**
3. URL: `{{base_url}}/users/auth/logout/`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):

```json
{
  "refresh_token": "{{refresh_token}}"
}
```

7. Click en **"Send"**
8. Respuesta esperada: **200 OK** con mensaje de logout exitoso

---

## 📊 PASO 8: Filtros y Búsqueda

### 8.1 Buscar Actividades

**Crear la petición:**

1. Add request → Nombre: **"Search Activities"**
2. Método: **GET**
3. URL: `{{base_url}}/activities/?search=English`
4. Authorization: **Bearer Token** → `{{access_token}}`
5. Click en **"Send"**

---

### 8.2 Filtrar Actividades Activas

**URL:** `{{base_url}}/activities/?is_active=true`

---

### 8.3 Filtrar Eventos por Actividad

**URL:** `{{base_url}}/events/?activity_code=ENG001`

---

### 8.4 Filtrar Eventos por Estado

**URL:** `{{base_url}}/events/?status=scheduled`

---

## 🎯 PASO 9: Orden de Pruebas Recomendado

Para probar el flujo completo, ejecuta las peticiones en este orden:

1. ✅ **Login - Teacher** (guarda tokens)
2. ✅ **Create Activity** (crea ENG001)
3. ✅ **List Activities** (verifica que se creó)
4. ✅ **Bulk Create Events** (crea eventos para ENG001)
5. ✅ **List Events** (copia un event_id)
6. ✅ **Login - Student** (cambia a estudiante)
7. ✅ **Enroll to Event** (inscríbete al evento)
8. ✅ **My Enrollments** (verifica inscripción)
9. ✅ **Login - Teacher** (vuelve a teacher)
10. ✅ **Event Enrollments** (ve quién está inscrito)
11. ✅ **Activity Statistics** (ve estadísticas)
12. ✅ **Logout**

---

## 🔧 Troubleshooting

### Error 401 Unauthorized
- **Causa:** Token expirado o inválido
- **Solución:** Ejecuta "Login" de nuevo o "Refresh Token"

### Error 403 Forbidden
- **Causa:** No tienes permisos (ej: student intentando crear actividad)
- **Solución:** Loguéate como teacher o admin

### Error 404 Not Found
- **Causa:** El recurso no existe (código de actividad incorrecto, etc.)
- **Solución:** Verifica que el código/ID sea correcto

### Error 400 Bad Request
- **Causa:** Datos inválidos en el body
- **Solución:** Revisa que el JSON esté bien formado y los campos sean correctos

---

## 💡 Tips Útiles

1. **Organiza las peticiones en carpetas:**
   - Autenticación
   - Usuarios
   - Actividades
   - Eventos

2. **Usa variables para IDs dinámicos:**
   - Guarda `event_id` o `activity_code` en variables de entorno

3. **Guarda la colección:**
   - File → Export → Guarda el JSON
   - Compártelo con tu equipo

4. **Usa el Console de Postman:**
   - View → Show Postman Console
   - Ve los logs de las peticiones

---

## ✅ Checklist de Verificación

- [ ] Login como Teacher funciona
- [ ] Login como Student funciona
- [ ] Crear actividad funciona
- [ ] Listar actividades funciona
- [ ] Crear eventos masivos funciona
- [ ] Inscribirse a evento funciona
- [ ] Ver mis inscripciones funciona
- [ ] Refresh token funciona
- [ ] Logout funciona

---

¡Listo! Ahora tienes una guía completa para probar toda la API con Postman. 🚀
