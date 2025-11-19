# Talkabout - Esquema de Base de Datos

## Entidades y Relaciones

### 1. User (Usuario)
Representa a todos los usuarios del sistema (administradores, profesores y estudiantes).

**Campos:**
- `id` (PK, UUID)
- `user_code` (String, único) - Código generado o USER_ID de edX (hash SHA-1)
- `email` (String, puede ser null) - Se borra al darse de baja
- `timezone` (String) - Zona horaria del usuario (ej: 'America/Mexico_City')
- `role` (Enum: 'admin', 'teacher', 'student')
- `is_active` (Boolean)
- `is_anonymized` (Boolean) - True si el usuario se dio de baja
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Índices:**
- `user_code` (único)
- `email` (único, cuando no es null)

---

### 2. Activity (Actividad)
Tarea de comunicación propuesta por un profesor.

**Campos:**
- `id` (PK, UUID)
- `code` (String, único) - Código para embeber en edX
- `title` (String)
- `description` (Text/HTML) - Descripción en formato HTML
- `max_participants_per_meeting` (Integer) - Máximo de participantes por reunión
- `created_by_id` (FK → User) - Profesor que creó la actividad
- `is_active` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relaciones:**
- `created_by`: ManyToOne → User (profesor)
- `files`: OneToMany → ActivityFile
- `events`: OneToMany → Event

**Índices:**
- `code` (único)
- `created_by_id`

---

### 3. ActivityFile (Archivo de Actividad)
Archivos adjuntos a una actividad.

**Campos:**
- `id` (PK, UUID)
- `activity_id` (FK → Activity)
- `file` (FileField) - Ruta al archivo
- `filename` (String) - Nombre original del archivo
- `uploaded_at` (DateTime)

**Relaciones:**
- `activity`: ManyToOne → Activity

**Índices:**
- `activity_id`

---

### 4. Event (Evento/Convocatoria)
Intervalo de tiempo concreto en el que realizar una actividad.

**Campos:**
- `id` (PK, UUID)
- `activity_id` (FK → Activity)
- `start_datetime` (DateTime, UTC) - Inicio del evento
- `end_datetime` (DateTime, UTC) - Fin del evento
- `waiting_time_minutes` (Integer, default: 10) - Tiempo de espera antes de crear reuniones
- `first_reminder_minutes` (Integer, nullable) - Minutos antes para 1er recordatorio
- `second_reminder_minutes` (Integer, nullable) - Minutos antes para 2do recordatorio
- `first_reminder_sent` (Boolean, default: False)
- `second_reminder_sent` (Boolean, default: False)
- `waiting_email_sent` (Boolean, default: False)
- `status` (Enum: 'scheduled', 'in_waiting', 'in_progress', 'completed', 'cancelled')
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relaciones:**
- `activity`: ManyToOne → Activity
- `enrollments`: OneToMany → Enrollment
- `meetings`: OneToMany → Meeting

**Índices:**
- `activity_id`
- `start_datetime`
- `status`

---

### 5. Enrollment (Inscripción)
Registro de un usuario inscrito a un evento.

**Campos:**
- `id` (PK, UUID)
- `user_id` (FK → User)
- `event_id` (FK → Event)
- `enrolled_at` (DateTime)
- `status` (Enum: 'enrolled', 'cancelled', 'attended', 'no_show')
- `unsubscribe_token` (String, único) - Token para enlace de baja
- `updated_at` (DateTime)

**Relaciones:**
- `user`: ManyToOne → User
- `event`: ManyToOne → Event

**Índices:**
- `user_id`, `event_id` (compuesto, único)
- `unsubscribe_token` (único)
- `status`

---

### 6. Meeting (Reunión)
Videoconferencia final donde varios usuarios trabajan la tarea.

**Campos:**
- `id` (PK, UUID)
- `event_id` (FK → Event)
- `meeting_url` (String) - URL de la videoconferencia
- `meeting_provider` (Enum: 'google_meet', 'jitsi')
- `meeting_id` (String) - ID del meeting en el proveedor
- `start_time` (DateTime)
- `end_time` (DateTime, nullable)
- `created_at` (DateTime)

**Relaciones:**
- `event`: ManyToOne → Event
- `participants`: OneToMany → MeetingParticipant

**Índices:**
- `event_id`
- `meeting_id`

---

### 7. MeetingParticipant (Participante de Reunión)
Relación entre usuarios y reuniones (tracking de asistencia real).

**Campos:**
- `id` (PK, UUID)
- `meeting_id` (FK → Meeting)
- `user_id` (FK → User)
- `joined_at` (DateTime) - Momento en que entró a la sala de espera
- `status` (Enum: 'waiting', 'joined', 'left')
- `updated_at` (DateTime)

**Relaciones:**
- `meeting`: ManyToOne → Meeting
- `user`: ManyToOne → User

**Índices:**
- `meeting_id`, `user_id` (compuesto, único)
- `status`

---

## Diagrama de Relaciones

```
User (1) ──────< (N) Activity
             created_by

Activity (1) ──────< (N) ActivityFile
Activity (1) ──────< (N) Event

Event (1) ──────< (N) Enrollment >────── (1) User
Event (1) ──────< (N) Meeting

Meeting (1) ──────< (N) MeetingParticipant >────── (1) User
```

---

## Notas Importantes

1. **Privacidad**: Cuando un usuario se da de baja:
   - Se elimina su `email`
   - Se cambia `user_code` a un código interno anónimo
   - Se marca `is_anonymized = True`
   - Se mantienen las estadísticas (enrollments, participations)

2. **Zonas Horarias**:
   - Todos los datetime se almacenan en UTC
   - El `timezone` del usuario se usa para mostrar fechas localizadas
   - Los eventos se crean en UTC pero el admin puede ver conversiones

3. **Códigos Únicos**:
   - `activity.code`: Para embeber en edX URLs
   - `user.user_code`: Identificador del usuario (generado o de edX)
   - `enrollment.unsubscribe_token`: Para enlaces de baja en emails

4. **Estados**:
   - Event status: scheduled → in_waiting → in_progress → completed
   - Enrollment status: enrolled → (cancelled | attended | no_show)
   - MeetingParticipant status: waiting → joined → left

5. **Algoritmo de Distribución**:
   - Se ejecuta cuando Event entra en estado 'in_waiting'
   - Se recogen usuarios con status='waiting' en MeetingParticipant
   - Se crean N meetings respetando max_participants_per_meeting
   - Cada meeting debe tener mínimo 2 participantes
