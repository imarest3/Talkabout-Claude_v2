# Talkabout API Documentation

## Base URL

```
http://localhost:8000/api/
```

---

## Authentication

All authenticated endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## User Authentication Endpoints

### 1. Register User (Normal)

Create a new user account with auto-generated user_code.

**Endpoint:** `POST /api/users/auth/register/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123!",
  "password_confirm": "securepass123!",
  "timezone": "America/Mexico_City"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid-here",
    "user_code": "user_a1b2c3d4e5f6",
    "email": "user@example.com",
    "timezone": "America/Mexico_City",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

---

### 2. Register User (from edX)

Register or retrieve a user from edX using their USER_ID.

**Endpoint:** `POST /api/users/auth/register/edx/`

**Authentication:** Not required

**Request Body:**
```json
{
  "edx_user_id": "original_edx_user_id_12345",
  "email": "edxuser@example.com",
  "timezone": "America/New_York"
}
```

**Note:** The `edx_user_id` will be hashed with SHA-1 before storing as `user_code`.

**Response (200 OK):**
```json
{
  "message": "User registered/retrieved successfully",
  "user": {
    "id": "uuid-here",
    "user_code": "bf42249b7def3276d81b71032fdcb637",
    "email": "edxuser@example.com",
    "timezone": "America/New_York",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

---

### 3. Login

Authenticate user and obtain JWT tokens.

**Endpoint:** `POST /api/users/auth/login/`

**Authentication:** Not required

**Request Body:**
```json
{
  "user_code": "user_a1b2c3d4e5f6",
  "password": "securepass123!"
}
```

**Response (200 OK):**
```json
{
  "access": "access_token_here",
  "refresh": "refresh_token_here",
  "user": {
    "id": "uuid-here",
    "user_code": "user_a1b2c3d4e5f6",
    "email": "user@example.com",
    "role": "student",
    "timezone": "America/Mexico_City"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 4. Logout

Logout user by blacklisting the refresh token.

**Endpoint:** `POST /api/users/auth/logout/`

**Authentication:** Required

**Request Body:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

### 5. Refresh Token

Get a new access token using a refresh token.

**Endpoint:** `POST /api/users/auth/token/refresh/`

**Authentication:** Not required

**Request Body:**
```json
{
  "refresh": "refresh_token_here"
}
```

**Response (200 OK):**
```json
{
  "access": "new_access_token_here",
  "refresh": "new_refresh_token_here"
}
```

---

## User Profile Endpoints

### 6. Get Profile

Get current user's profile information.

**Endpoint:** `GET /api/users/profile/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": "uuid-here",
  "user_code": "user_a1b2c3d4e5f6",
  "email": "user@example.com",
  "timezone": "America/Mexico_City",
  "role": "student",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### 7. Update Profile

Update current user's profile (email and timezone).

**Endpoint:** `PUT /api/users/profile/update/` or `PATCH /api/users/profile/update/`

**Authentication:** Required

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "timezone": "Europe/Madrid"
}
```

**Response (200 OK):**
```json
{
  "email": "newemail@example.com",
  "timezone": "Europe/Madrid"
}
```

---

### 8. Change Password

Change current user's password.

**Endpoint:** `POST /api/users/profile/change-password/`

**Authentication:** Required

**Request Body:**
```json
{
  "old_password": "oldpass123!",
  "new_password": "newsecurepass456!",
  "new_password_confirm": "newsecurepass456!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "old_password": ["Old password is incorrect."]
}
```

---

### 9. Anonymize User

Anonymize user data for GDPR compliance. Removes email and replaces user_code with anonymous ID, while keeping statistics.

**Endpoint:** `POST /api/users/profile/anonymize/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "message": "User data anonymized successfully. You have been logged out."
}
```

**Note:** After anonymization:
- User's email is set to `null`
- User's user_code is changed to `anonymous_<uuid>`
- User is marked as inactive
- All enrollment and participation statistics are preserved

---

## User Roles

The system has three user roles:

1. **student** (default) - Can enroll in events and participate in meetings
2. **teacher** - Can create and manage activities and events
3. **admin** - Full access to all resources

---

## Common Status Codes

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required or failed
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

---

## Error Response Format

All error responses follow this format:

```json
{
  "field_name": ["Error message"],
  "another_field": ["Another error message"]
}
```

Or for general errors:

```json
{
  "detail": "Error message",
  "error": "Error description"
}
```

---

## Testing Endpoints

You can test these endpoints using:

### cURL Example:

```bash
# Register user
curl -X POST http://localhost:8000/api/users/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123!",
    "password_confirm": "testpass123!",
    "timezone": "UTC"
  }'

# Login
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_code": "user_a1b2c3d4e5f6",
    "password": "testpass123!"
  }'

# Get profile (authenticated)
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <your_access_token>"
```

### Postman / Insomnia

Import the endpoints and configure:
1. Base URL: `http://localhost:8000/api/`
2. For authenticated requests, add header: `Authorization: Bearer <access_token>`

---

## Activities Management Endpoints

### 10. List Activities

Get a list of all activities with filtering and search capabilities.

**Endpoint:** `GET /api/activities/`

**Authentication:** Required

**Query Parameters:**
- `search` - Search in code, title, or description
- `is_active` - Filter by active status (`true` or `false`)
- `created_by` - Filter by creator user ID
- `ordering` - Sort by field (e.g., `-created_at`, `title`, `code`)

**Visibility Rules:**
- **Students**: Only see active activities
- **Teachers**: See their own activities + active ones
- **Admins**: See all activities

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "code": "ACT001",
      "title": "Conversation Practice",
      "description": "<p>Practice speaking English</p>",
      "max_participants_per_meeting": 6,
      "created_by": "uuid-teacher",
      "created_by_name": "teacher_001",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "files": [
        {
          "id": "uuid-file",
          "filename": "Instructions.pdf",
          "file": "/media/activity_files/2024/01/15/instructions.pdf",
          "file_url": "http://localhost:8000/media/activity_files/2024/01/15/instructions.pdf",
          "uploaded_at": "2024-01-15T10:35:00Z"
        }
      ],
      "event_count": 5
    }
  ]
}
```

---

### 11. Create Activity

Create a new activity. Only teachers and admins can create activities.

**Endpoint:** `POST /api/activities/create/`

**Authentication:** Required (Teacher or Admin only)

**Request Body:**
```json
{
  "code": "ACT002",
  "title": "Group Discussion",
  "description": "<p>Discussion activity about technology</p>",
  "max_participants_per_meeting": 8,
  "is_active": true
}
```

**Validation:**
- `code` must be unique
- `max_participants_per_meeting` must be at least 2
- `created_by` is automatically set to current user

**Response (201 Created):**
```json
{
  "code": "ACT002",
  "title": "Group Discussion",
  "description": "<p>Discussion activity about technology</p>",
  "max_participants_per_meeting": 8,
  "is_active": true
}
```

---

### 12. Get Activity Details

Get detailed information about a specific activity.

**Endpoint:** `GET /api/activities/<code>/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": "uuid-here",
  "code": "ACT001",
  "title": "Conversation Practice",
  "description": "<p>Practice speaking English</p>",
  "max_participants_per_meeting": 6,
  "created_by": "uuid-teacher",
  "created_by_name": "teacher_001",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "files": [],
  "event_count": 5
}
```

---

### 13. Update Activity

Update an existing activity. Only the creator or admins can update.

**Endpoint:** `PUT /api/activities/<code>/update/` or `PATCH /api/activities/<code>/update/`

**Authentication:** Required (Creator or Admin only)

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "<p>Updated description</p>",
  "max_participants_per_meeting": 10,
  "is_active": true,
  "code": "ACT001"
}
```

**Response (200 OK):**
```json
{
  "code": "ACT001",
  "title": "Updated Title",
  "description": "<p>Updated description</p>",
  "max_participants_per_meeting": 10,
  "is_active": true
}
```

---

### 14. Delete Activity

Delete an activity. Only the creator or admins can delete.

**Endpoint:** `DELETE /api/activities/<code>/delete/`

**Authentication:** Required (Creator or Admin only)

**Behavior:**
- If activity has events: **Soft delete** (marks as inactive)
- If activity has no events: **Hard delete** (removes from database)

**Response (200 OK - Soft Delete):**
```json
{
  "message": "Activity marked as inactive (has associated events)"
}
```

**Response (204 No Content - Hard Delete):**
```json
{
  "message": "Activity deleted successfully"
}
```

---

### 15. Upload File to Activity

Upload a file attachment to an activity.

**Endpoint:** `POST /api/activities/<code>/files/upload/`

**Authentication:** Required (Creator or Admin only)

**Request Body (multipart/form-data):**
```
file: <binary file data>
filename: "Instructions Document"
```

**File Validation:**
- Maximum file size: 10MB
- `filename` is optional (auto-filled from file if not provided)

**Response (201 Created):**
```json
{
  "id": "uuid-file",
  "filename": "Instructions Document",
  "file": "/media/activity_files/2024/01/15/instructions.pdf",
  "file_url": "http://localhost:8000/media/activity_files/2024/01/15/instructions.pdf",
  "uploaded_at": "2024-01-15T10:35:00Z"
}
```

---

### 16. Delete File from Activity

Delete a file attachment from an activity.

**Endpoint:** `DELETE /api/activities/<code>/files/<file_id>/delete/`

**Authentication:** Required (Creator or Admin only)

**Response (204 No Content):**
```json
{
  "message": "File deleted successfully"
}
```

---

### 17. Get Activity Statistics

Get statistics for an activity (event count, enrollments, attendance).

**Endpoint:** `GET /api/activities/<code>/statistics/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "activity_code": "ACT001",
  "activity_title": "Conversation Practice",
  "total_events": 10,
  "active_events": 3,
  "completed_events": 7,
  "total_enrollments": 45,
  "currently_enrolled": 15,
  "total_attended": 38,
  "attendance_rate": 84.44
}
```

---

## Next API Sections (Coming Soon)

- Events Management
- Enrollments
- Meetings and Video Conferences

## Events Management Endpoints

### 18. List Events

Get a list of all events with filtering capabilities.

**Endpoint:** `GET /api/events/`

**Authentication:** Required

**Query Parameters:**
- `activity_code` - Filter by activity code
- `status` - Filter by event status (scheduled, in_waiting, in_progress, completed, cancelled)
- `start_date` - Filter events starting from this date (ISO format)
- `end_date` - Filter events up to this date (ISO format)
- `search` - Search in activity code or title
- `ordering` - Sort by field (e.g., `start_datetime`, `-created_at`)

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "activity": "uuid-activity",
      "activity_code": "ACT001",
      "activity_title": "Conversation Practice",
      "start_datetime": "2024-02-01T09:00:00Z",
      "end_datetime": "2024-02-01T10:00:00Z",
      "waiting_time_minutes": 10,
      "first_reminder_minutes": 1440,
      "second_reminder_minutes": 60,
      "first_reminder_sent": false,
      "second_reminder_sent": false,
      "waiting_email_sent": false,
      "status": "scheduled",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "enrolled_count": 12,
      "attended_count": 0
    }
  ]
}
```

---

### 19. Create Event

Create a single event for an activity.

**Endpoint:** `POST /api/events/`

**Authentication:** Required (Teacher or Admin only)

**Request Body:**
```json
{
  "activity_code": "ACT001",
  "start_datetime": "2024-02-01T09:00:00Z",
  "end_datetime": "2024-02-01T10:00:00Z",
  "waiting_time_minutes": 10,
  "first_reminder_minutes": 1440,
  "second_reminder_minutes": 60
}
```

**Validation:**
- `start_datetime` must be in the future
- `end_datetime` must be after `start_datetime`
- `first_reminder_minutes` must be greater than `second_reminder_minutes`

**Response (201 Created):**
```json
{
  "id": "uuid-here",
  "activity": "uuid-activity",
  "activity_code": "ACT001",
  "activity_title": "Conversation Practice",
  "start_datetime": "2024-02-01T09:00:00Z",
  "end_datetime": "2024-02-01T10:00:00Z",
  "waiting_time_minutes": 10,
  "first_reminder_minutes": 1440,
  "second_reminder_minutes": 60,
  "status": "scheduled"
}
```

---

### 20. Bulk Create Events

Create multiple events based on date range and time slots.

**Endpoint:** `POST /api/events/bulk-create/`

**Authentication:** Required (Teacher or Admin only)

**Request Body:**
```json
{
  "activity_code": "ACT001",
  "start_date": "2024-02-01",
  "end_date": "2024-02-07",
  "hours_utc": ["09:00", "14:00", "18:00"],
  "duration_minutes": 60,
  "waiting_time_minutes": 10,
  "first_reminder_minutes": 1440,
  "second_reminder_minutes": 60
}
```

**Description:**
- Creates events for each day in the date range
- For each day, creates events at specified hours (in UTC)
- Skips events in the past

**Response (201 Created):**
```json
{
  "message": "Successfully created 21 events",
  "events": [
    {
      "id": "uuid-1",
      "activity_code": "ACT001",
      "start_datetime": "2024-02-01T09:00:00Z",
      "end_datetime": "2024-02-01T10:00:00Z"
    },
    ...
  ]
}
```

---

### 21. Get Event Details

Get detailed information about a specific event.

**Endpoint:** `GET /api/events/<event_id>/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": "uuid-here",
  "activity": "uuid-activity",
  "activity_code": "ACT001",
  "activity_title": "Conversation Practice",
  "start_datetime": "2024-02-01T09:00:00Z",
  "end_datetime": "2024-02-01T10:00:00Z",
  "waiting_time_minutes": 10,
  "first_reminder_minutes": 1440,
  "second_reminder_minutes": 60,
  "status": "scheduled",
  "enrolled_count": 12,
  "attended_count": 0
}
```

---

### 22. Update Event

Update an event. Cannot update events that have already started.

**Endpoint:** `PUT /api/events/<event_id>/update/` or `PATCH /api/events/<event_id>/update/`

**Authentication:** Required (Teacher or Admin only)

**Request Body:**
```json
{
  "start_datetime": "2024-02-01T10:00:00Z",
  "end_datetime": "2024-02-01T11:00:00Z",
  "waiting_time_minutes": 15
}
```

**Response (200 OK):**
```json
{
  "start_datetime": "2024-02-01T10:00:00Z",
  "end_datetime": "2024-02-01T11:00:00Z",
  "waiting_time_minutes": 15
}
```

---

### 23. Delete Event

Delete an event. Cannot delete events with enrollments.

**Endpoint:** `DELETE /api/events/<event_id>/delete/`

**Authentication:** Required (Teacher or Admin only)

**Response (204 No Content):**
```json
{
  "message": "Event deleted successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Cannot delete events with enrollments. Cancel the event instead."
}
```

---

### 24. Enroll in Event

Enroll current user in an event.

**Endpoint:** `POST /api/events/enroll/`

**Authentication:** Required

**Request Body:**
```json
{
  "event_id": "uuid-here"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-enrollment",
  "user": "uuid-user",
  "user_code": "student_001",
  "event": "uuid-event",
  "event_id": "uuid-event",
  "event_start": "2024-02-01T09:00:00Z",
  "event_end": "2024-02-01T10:00:00Z",
  "activity_code": "ACT001",
  "activity_title": "Conversation Practice",
  "enrolled_at": "2024-01-20T15:30:00Z",
  "status": "enrolled"
}
```

---

### 25. Unenroll from Event

Unenroll current user from an event.

**Endpoint:** `POST /api/events/<event_id>/unenroll/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "message": "Successfully unenrolled from event"
}
```

---

### 26. My Enrollments

Get current user's enrollments.

**Endpoint:** `GET /api/events/my-enrollments/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-enrollment",
      "event_id": "uuid-event",
      "event_start": "2024-02-01T09:00:00Z",
      "event_end": "2024-02-01T10:00:00Z",
      "activity_code": "ACT001",
      "activity_title": "Conversation Practice",
      "status": "enrolled",
      "enrolled_at": "2024-01-20T15:30:00Z"
    }
  ]
}
```

---

### 27. Get Event Enrollments

Get all enrollments for a specific event (Teachers and Admins only).

**Endpoint:** `GET /api/events/<event_id>/enrollments/`

**Authentication:** Required (Teacher or Admin only)

**Response (200 OK):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-enrollment",
      "user_code": "student_001",
      "status": "enrolled",
      "enrolled_at": "2024-01-20T15:30:00Z"
    }
  ]
}
```

---

### 28. Convert Timezone

Convert a UTC datetime to a target timezone.

**Endpoint:** `POST /api/events/convert-timezone/`

**Authentication:** Required

**Request Body:**
```json
{
  "datetime_utc": "2024-02-01T14:00:00Z",
  "target_timezone": "America/Mexico_City"
}
```

**Response (200 OK):**
```json
{
  "datetime_utc": "2024-02-01T14:00:00+00:00",
  "datetime_local": "2024-02-01T08:00:00-06:00",
  "timezone": "America/Mexico_City",
  "offset": "-0600"
}
```

---

### 29. Get Event Statistics

Get statistics for a specific event.

**Endpoint:** `GET /api/events/<event_id>/statistics/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "event_id": "uuid-here",
  "activity_code": "ACT001",
  "activity_title": "Conversation Practice",
  "start_datetime": "2024-02-01T09:00:00Z",
  "end_datetime": "2024-02-01T10:00:00Z",
  "status": "scheduled",
  "total_enrolled": 15,
  "total_cancelled": 2,
  "total_attended": 0,
  "total_no_show": 0,
  "max_participants_per_meeting": 6,
  "meetings_count": 0
}
```

---

## Next API Sections (Coming Soon)

- Meetings and Video Conferences
