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

## Next API Sections (Coming Soon)

- Activities Management
- Events Management
- Enrollments
- Meetings and Video Conferences
- Statistics and Reporting
