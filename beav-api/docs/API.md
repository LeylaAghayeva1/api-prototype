# beav API v1: API Documentation

beav is a volunteer registration platform. This prototype exposes one main resource, **registration forms**, through a REST API that uses mocked in-memory data.

- **Base URL (local):** `http://127.0.0.1:8000`
- **API prefix:** `/api/v1`
- **Interactive docs (Swagger UI):** `http://127.0.0.1:8000/docs`
- **Data:** in memory, and **resets every time the server restarts**

---

## Contents

1. [Authentication](#1-authentication)
2. [Authorization rules](#2-authorization-rules)
3. [Response format](#3-response-format)
4. [Error codes](#4-error-codes)
5. [The Form resource](#5-the-form-resource)
6. [Validation rules](#6-validation-rules)
7. [Endpoints](#7-endpoints)
   - [GET /api/v1/forms](#71-list-forms): list forms
   - [GET /api/v1/forms/{form_id}](#72-get-one-form): get one form
   - [POST /api/v1/forms](#73-create-a-form): create a form
   - [PUT /api/v1/forms/{form_id}](#74-update-a-form): update a form
   - [DELETE /api/v1/forms/{form_id}](#75-delete-a-form): delete a form
   - [GET /api/v1/greeting](#76-greeting-page): HTML greeting page
8. [Mock data](#8-mock-data)

---

## 1. Authentication

There is no real login in this prototype. Every request to `/api/v1/forms` must send one of three predefined tokens in the `Authorization` header:

```http
Authorization: Bearer user-a-token
```

| User | Token | Role | Permissions |
|---|---|---|---|
| User A (organization member, "Green Baku") | `user-a-token` | `member` | Manages only their own forms |
| User B (organization member, "Help Ganja") | `user-b-token` | `member` | Manages only their own forms |
| Platform Administrator | `admin-token` | `admin` | Manages all forms |

A request gets **`401 Unauthorized`** when:

| Case | Example header | Message |
|---|---|---|
| Header is missing | *(none)* | `Authentication token is missing. Send 'Authorization: Bearer <token>'.` |
| Header is not in `Bearer <token>` format | `Authorization: user-a-token` | `Authorization header must be in the format 'Bearer <token>'.` |
| Token is not one of the three above | `Authorization: Bearer abc` | `Authentication token is invalid.` |

401 responses also include the header `WWW-Authenticate: Bearer`.

The token is checked **before** anything else, so a request with a bad token always gets 401, even if its body is also invalid.

---

## 2. Authorization rules

| Action | User A / User B | Admin |
|---|---|---|
| List forms | Sees **only their own** forms | Sees **all** forms |
| Read one form | Only their own | Any form |
| Create a form | Yes; the new form is owned by them | Yes; the new form is owned by `admin` |
| Update a form | Only their own | Any form (the owner does not change) |
| Delete a form | Only their own | Any form |

### Why we return `404` instead of `403` for another user's form

When User A asks for a form that belongs to User B, the API answers **`404 Not Found`**, exactly as if the form did not exist.

- A `403 Forbidden` would confirm that the form **exists** and only access is denied. That leaks information about other organizations (for example, that a form ID is in use).
- A `404` reveals nothing. User A cannot tell "this belongs to someone else" apart from "this doesn't exist".
- This follows our proposal's privacy requirement **FR-14**: *restrict access to personal data and individual applications to authorized users*.

The ownership check also runs **before** the duplicate-title check, so User A cannot learn User B's form titles through a `409` either.

---

## 3. Response format

Every JSON response uses the same envelope. The HTTP status code always matches it: `2xx` means `success: true`, and `4xx`/`5xx` means `success: false`.

**Success**
```json
{
  "success": true,
  "message": "Form created successfully.",
  "data": { "id": "form_106", "title": "Park Cleanup Day", "...": "..." }
}
```
- `data` holds one form, a list of forms, or `null` (after delete).
- List responses also include `meta`:
  ```json
  "meta": { "total": 5, "page": 1, "perPage": 10 }
  ```

**Error**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid or missing fields.",
    "details": [
      { "field": "title", "message": "String should have at least 3 characters" }
    ]
  }
}
```
- `error.code` is always one of the fixed codes in [section 4](#4-error-codes).
- `details` appears **only** for validation errors, with one entry per problem field.
- Error messages never include stack traces, file paths or other internal details. Unexpected server errors are logged on the server and return a generic `500` message.

---

## 4. Error codes

| HTTP status | `error.code` | When it happens |
|---:|---|---|
| `400` | `VALIDATION_ERROR` | Body or query parameters are invalid, missing, of the wrong type, or contain unknown fields; body is not valid JSON |
| `401` | `UNAUTHORIZED` | Token is missing, malformed or invalid |
| `404` | `NOT_FOUND` | Form does not exist, **or** belongs to another user; also unknown URLs |
| `405` | `METHOD_NOT_ALLOWED` | HTTP method not supported for the endpoint (e.g. `PATCH`) |
| `409` | `CONFLICT` | The owner already has a form with the same title |
| `500` | `INTERNAL_ERROR` | Unexpected server error (safe, generic message) |

---

## 5. The Form resource

A **form** is a volunteer registration form created by an organization: information about the volunteering opportunity, plus the questions volunteers must answer.

```json
{
  "id": "form_101",
  "title": "Beach Cleanup Volunteers",
  "description": "Help us clean Bilgah beach before winter.",
  "location": "Baku",
  "eventDate": "2026-12-05",
  "capacity": 40,
  "status": "published",
  "questions": [
    { "label": "Full name", "type": "text", "required": true },
    { "label": "Phone number", "type": "text", "required": true },
    { "label": "Do you have a car?", "type": "yes_no", "required": false }
  ],
  "ownerId": "user-a",
  "createdAt": "2026-11-01T10:00:00Z",
  "updatedAt": "2026-11-01T10:00:00Z"
}
```

| Field | Type | Set by | Description |
|---|---|---|---|
| `id` | string | server | Unique ID, e.g. `form_101` |
| `title` | string | client | Name of the opportunity |
| `description` | string or null | client | Details for volunteers |
| `location` | string or null | client | City or place |
| `eventDate` | string (`YYYY-MM-DD`) | client | Date of the event |
| `capacity` | integer | client | Maximum number of volunteers |
| `status` | `draft` / `published` / `closed` | client | Form lifecycle (FR-03: create, publish, close) |
| `questions` | array of Question | client | Questions volunteers answer |
| `ownerId` | string | server (from token) | User who owns the form |
| `createdAt` | string (UTC timestamp) | server | When the form was created |
| `updatedAt` | string (UTC timestamp) | server | When the form was last changed |

**Question**

| Field | Type | Description |
|---|---|---|
| `label` | string | The question text, e.g. "Full name" |
| `type` | `text` / `yes_no` / `number` | Kind of answer expected |
| `required` | boolean | Whether the volunteer must answer it |

Volunteer answers (submissions) are planned as a separate resource for a later version.

---

## 6. Validation rules

These rules apply to the request body of **POST** and **PUT**. Every failure returns `400 VALIDATION_ERROR` with a `details` entry naming the field.

| Field | Required | Rules |
|---|---|---|
| `title` | yes | string, 3–100 characters; leading/trailing spaces are removed, so a title of only spaces fails |
| `description` | no | string, at most 1000 characters |
| `location` | no | string, at most 100 characters |
| `eventDate` | yes | a real calendar date in `YYYY-MM-DD` format (`2026-02-30` is rejected) |
| `capacity` | yes | whole number from 1 to 10000 |
| `status` | no (default `draft`) | one of `draft`, `published`, `closed` |
| `questions` | yes | list of 1–50 questions |
| `questions[].label` | yes | string, 1–200 characters |
| `questions[].type` | no (default `text`) | one of `text`, `yes_no`, `number` |
| `questions[].required` | no (default `false`) | boolean |

**Additional rules**

- **Strict types.** Values are not converted: `"capacity": "30"` (text) and `"capacity": true` are rejected, and so is `"required": "yes"`.
- **Unknown fields are rejected.** Any field not listed above returns `"This field is not allowed."` This includes the server-controlled fields `id`, `ownerId`, `createdAt` and `updatedAt`, so a client can never create a form in another user's name.
- **Body must be a JSON object.** Invalid JSON, an empty body, or a JSON array returns `400`.
- **Unique titles per owner.** One owner cannot have two forms with the same title (capital letters are ignored). This returns `409 CONFLICT`, not `400`, because the request itself is valid but clashes with existing data. Different owners may use the same title.

---

## 7. Endpoints

| Method | Path | Description | Auth | Success |
|---|---|---|---|---|
| `GET` | `/api/v1/forms` | List forms | any token | `200` |
| `GET` | `/api/v1/forms/{form_id}` | Get one form | any token | `200` |
| `POST` | `/api/v1/forms` | Create a form | any token | `201` |
| `PUT` | `/api/v1/forms/{form_id}` | Update (replace) a form | any token | `200` |
| `DELETE` | `/api/v1/forms/{form_id}` | Delete a form | any token | `200` |
| `GET` | `/api/v1/greeting` | HTML greeting page | none | `200` |

---

### 7.1 List forms

```http
GET /api/v1/forms
```

Returns the forms the caller can see: their own forms, or **all** forms for the admin. Supports pagination and filtering by status.

**Headers**

| Header | Required | Value |
|---|---|---|
| `Authorization` | yes | `Bearer <token>`; any of the three users |

**Query parameters**

| Name | Type | Default | Rules | Description |
|---|---|---|---|---|
| `page` | integer | `1` | ≥ 1 | Page number |
| `perPage` | integer | `10` | 1–100 | Forms per page |
| `status` | string | *(none)* | `draft`, `published`, `closed` | Only return forms with this status |

A `page` past the last page returns an empty `data` list (still `200`). Unknown query parameters are ignored.

**Success: `200 OK`**, with `meta`

**Errors**

| Status | Code | Cause |
|---:|---|---|
| 400 | `VALIDATION_ERROR` | `page` < 1, `perPage` outside 1–100, non-numeric `page`/`perPage`, invalid `status` |
| 401 | `UNAUTHORIZED` | Missing, malformed or invalid token |
| 405 | `METHOD_NOT_ALLOWED` | e.g. `PATCH /api/v1/forms` |

**Example request**
```http
GET /api/v1/forms?page=1&perPage=2
Authorization: Bearer user-a-token
```

**Example response: `200 OK`**
```json
{
  "success": true,
  "message": "2 form(s) found.",
  "data": [
    {
      "id": "form_101",
      "title": "Beach Cleanup Volunteers",
      "description": "Help us clean Bilgah beach before winter.",
      "location": "Baku",
      "eventDate": "2026-12-05",
      "capacity": 40,
      "status": "published",
      "questions": [
        { "label": "Full name", "type": "text", "required": true },
        { "label": "Phone number", "type": "text", "required": true },
        { "label": "Do you have a car?", "type": "yes_no", "required": false }
      ],
      "ownerId": "user-a",
      "createdAt": "2026-11-01T10:00:00Z",
      "updatedAt": "2026-11-01T10:00:00Z"
    },
    {
      "id": "form_102",
      "title": "Tree Planting Day",
      "description": "Plant 500 trees in Sumgait park.",
      "location": "Sumgait",
      "eventDate": "2027-03-21",
      "capacity": 100,
      "status": "draft",
      "questions": [
        { "label": "Full name", "type": "text", "required": true },
        { "label": "T-shirt size", "type": "text", "required": false }
      ],
      "ownerId": "user-a",
      "createdAt": "2026-11-03T09:30:00Z",
      "updatedAt": "2026-11-03T09:30:00Z"
    }
  ],
  "meta": { "total": 2, "page": 1, "perPage": 2 }
}
```

**Example error: `400` (invalid query parameter)**
```http
GET /api/v1/forms?perPage=500
Authorization: Bearer user-a-token
```
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid or missing fields.",
    "details": [
      { "field": "perPage", "message": "Input should be less than or equal to 100" }
    ]
  }
}
```

---

### 7.2 Get one form

```http
GET /api/v1/forms/{form_id}
```

**Headers:** `Authorization: Bearer <token>` (required; owner or admin)

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `form_id` | string | ID of the form, e.g. `form_101` |

**Success: `200 OK`**, with the form in `data`

**Errors**

| Status | Code | Cause |
|---:|---|---|
| 401 | `UNAUTHORIZED` | Missing, malformed or invalid token |
| 404 | `NOT_FOUND` | Form does not exist, or belongs to another user (see [section 2](#2-authorization-rules)) |
| 405 | `METHOD_NOT_ALLOWED` | e.g. `PATCH` or `POST` on this path |

**Example request**
```http
GET /api/v1/forms/form_101
Authorization: Bearer user-a-token
```

**Example response: `200 OK`**
```json
{
  "success": true,
  "message": "Form retrieved successfully.",
  "data": {
    "id": "form_101",
    "title": "Beach Cleanup Volunteers",
    "description": "Help us clean Bilgah beach before winter.",
    "location": "Baku",
    "eventDate": "2026-12-05",
    "capacity": 40,
    "status": "published",
    "questions": [
      { "label": "Full name", "type": "text", "required": true },
      { "label": "Phone number", "type": "text", "required": true },
      { "label": "Do you have a car?", "type": "yes_no", "required": false }
    ],
    "ownerId": "user-a",
    "createdAt": "2026-11-01T10:00:00Z",
    "updatedAt": "2026-11-01T10:00:00Z"
  }
}
```

**Example error: `404` (another user's form, or a non-existent ID)**
```http
GET /api/v1/forms/form_103
Authorization: Bearer user-a-token
```
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Form with id 'form_103' was not found."
  }
}
```

---

### 7.3 Create a form

```http
POST /api/v1/forms
```

Creates a new form. The owner is **always** the user from the token. A new ID (`form_106`, `form_107`, …) and timestamps are set by the server.

**Headers**

| Header | Required | Value |
|---|---|---|
| `Authorization` | yes | `Bearer <token>`; any of the three users |
| `Content-Type` | yes | `application/json` |

**Body:** a Form without the server fields. See [section 6](#6-validation-rules) for all rules.

**Success: `201 Created`**, with the new form in `data`

**Errors**

| Status | Code | Cause |
|---:|---|---|
| 400 | `VALIDATION_ERROR` | Missing/invalid fields, wrong types, unknown fields, invalid JSON |
| 401 | `UNAUTHORIZED` | Missing, malformed or invalid token |
| 405 | `METHOD_NOT_ALLOWED` | e.g. `POST /api/v1/forms/form_101` |
| 409 | `CONFLICT` | Caller already has a form with this title |

**Example request**
```http
POST /api/v1/forms
Authorization: Bearer user-a-token
Content-Type: application/json
```
```json
{
  "title": "Park Cleanup Day",
  "description": "Collect litter in Ganjlik park.",
  "location": "Baku",
  "eventDate": "2026-12-20",
  "capacity": 30,
  "status": "published",
  "questions": [
    { "label": "Full name", "type": "text", "required": true },
    { "label": "Do you have gloves?", "type": "yes_no", "required": false }
  ]
}
```

**Example response: `201 Created`**
```json
{
  "success": true,
  "message": "Form created successfully.",
  "data": {
    "id": "form_106",
    "title": "Park Cleanup Day",
    "description": "Collect litter in Ganjlik park.",
    "location": "Baku",
    "eventDate": "2026-12-20",
    "capacity": 30,
    "status": "published",
    "questions": [
      { "label": "Full name", "type": "text", "required": true },
      { "label": "Do you have gloves?", "type": "yes_no", "required": false }
    ],
    "ownerId": "user-a",
    "createdAt": "2026-11-21T06:36:28Z",
    "updatedAt": "2026-11-21T06:36:28Z"
  }
}
```

**Example error: `400` (several problems at once)**
```json
{ "title": "Hi", "eventDate": "2026-12-20", "capacity": "30", "ownerId": "user-b",
  "questions": [{ "label": "Full name" }] }
```
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid or missing fields.",
    "details": [
      { "field": "title", "message": "String should have at least 3 characters" },
      { "field": "capacity", "message": "Input should be a valid integer" },
      { "field": "ownerId", "message": "This field is not allowed." }
    ]
  }
}
```

**Example error: `400` (invalid JSON)**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid or missing fields.",
    "details": [
      { "field": "body", "message": "The request body is not valid JSON." }
    ]
  }
}
```

**Example error: `409` (duplicate title)**: User A already owns `form_101` "Beach Cleanup Volunteers":
```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "A form titled 'Beach Cleanup Volunteers' already exists for this owner."
  }
}
```

---

### 7.4 Update a form

```http
PUT /api/v1/forms/{form_id}
```

**Replaces** all editable fields of a form, so the body must be a **complete** form with the same rules as create. `id`, `ownerId` and `createdAt` never change. When the admin edits User A's form, the form still belongs to User A. `updatedAt` is set to the current time.

**Headers**

| Header | Required | Value |
|---|---|---|
| `Authorization` | yes | `Bearer <token>`; owner or admin |
| `Content-Type` | yes | `application/json` |

**Path parameters:** `form_id` (string): ID of the form to update

**Body:** same as [Create](#73-create-a-form); all required fields must be present.

**Success: `200 OK`**, with the updated form in `data`

**Errors**

| Status | Code | Cause |
|---:|---|---|
| 400 | `VALIDATION_ERROR` | Missing/invalid fields, wrong types, unknown fields (including `id`, `ownerId`), invalid JSON |
| 401 | `UNAUTHORIZED` | Missing, malformed or invalid token |
| 404 | `NOT_FOUND` | Form does not exist, or belongs to another user |
| 405 | `METHOD_NOT_ALLOWED` | e.g. `PUT /api/v1/forms` (without an ID) |
| 409 | `CONFLICT` | The form's owner already has **another** form with this title (saving a form with its own unchanged title is allowed) |

**Order of checks:** token (401) → body (400) → form exists and caller may access it (404) → duplicate title (409).

**Example request**
```http
PUT /api/v1/forms/form_106
Authorization: Bearer user-a-token
Content-Type: application/json
```
```json
{
  "title": "Park Cleanup Day (updated)",
  "description": "Collect litter in Ganjlik park.",
  "location": "Baku",
  "eventDate": "2026-12-20",
  "capacity": 45,
  "status": "published",
  "questions": [
    { "label": "Full name", "type": "text", "required": true },
    { "label": "Do you have gloves?", "type": "yes_no", "required": false }
  ]
}
```

**Example response: `200 OK`**
```json
{
  "success": true,
  "message": "Form updated successfully.",
  "data": {
    "id": "form_106",
    "title": "Park Cleanup Day (updated)",
    "description": "Collect litter in Ganjlik park.",
    "location": "Baku",
    "eventDate": "2026-12-20",
    "capacity": 45,
    "status": "published",
    "questions": [
      { "label": "Full name", "type": "text", "required": true },
      { "label": "Do you have gloves?", "type": "yes_no", "required": false }
    ],
    "ownerId": "user-a",
    "createdAt": "2026-11-21T06:36:28Z",
    "updatedAt": "2026-11-21T06:40:12Z"
  }
}
```

**Example error: `404` (User B tries to update User A's form)**
```http
PUT /api/v1/forms/form_101
Authorization: Bearer user-b-token
```
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Form with id 'form_101' was not found."
  }
}
```

---

### 7.5 Delete a form

```http
DELETE /api/v1/forms/{form_id}
```

**Headers:** `Authorization: Bearer <token>` (required; owner or admin)

**Path parameters:** `form_id` (string): ID of the form to delete

**Success: `200 OK`**, with `data: null`. Deleted IDs are never reused.

**Errors**

| Status | Code | Cause |
|---:|---|---|
| 401 | `UNAUTHORIZED` | Missing, malformed or invalid token |
| 404 | `NOT_FOUND` | Form does not exist (including already deleted), or belongs to another user |
| 405 | `METHOD_NOT_ALLOWED` | e.g. `DELETE /api/v1/forms` (without an ID) |

**Example request**
```http
DELETE /api/v1/forms/form_106
Authorization: Bearer user-a-token
```

**Example response: `200 OK`**
```json
{
  "success": true,
  "message": "Form deleted successfully.",
  "data": null
}
```

**Example error: `401` (no token)**
```http
DELETE /api/v1/forms/form_106
```
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication token is missing. Send 'Authorization: Bearer <token>'."
  }
}
```

**Example error: `405` (unsupported method)**
```http
PATCH /api/v1/forms/form_101
Authorization: Bearer user-a-token
```
```json
{
  "success": false,
  "error": {
    "code": "METHOD_NOT_ALLOWED",
    "message": "This HTTP method is not supported for this endpoint."
  }
}
```

---

### 7.6 Greeting page

```http
GET /api/v1/greeting
```

Returns an **HTML page**, not JSON. Open it in a browser. It shows the project name and description, who it is for, the team members with student IDs and contributions, every available endpoint, and the API status and version. The page is styled and adapts to desktop and mobile screens.

**Headers:** none required (no token needed)

**Success: `200 OK`**

```http
Content-Type: text/html; charset=utf-8
```

**Errors**

| Status | Code | Cause |
|---:|---|---|
| 405 | `METHOD_NOT_ALLOWED` | Any method other than `GET` (returns a JSON error envelope) |

**Example request**
```http
GET /api/v1/greeting
```

**Example response (shortened)**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>beav API</title>
  ...
</head>
<body>
  <span class="status">API is running · v1</span>
  <h1>Welcome to beav</h1>
  ...
</body>
</html>
```

---

## 8. Mock data

Data is stored in memory (`app/data.py`) and **resets when the server restarts**.

| ID | Title | Owner | Status |
|---|---|---|---|
| `form_101` | Beach Cleanup Volunteers | user-a | published |
| `form_102` | Tree Planting Day | user-a | draft |
| `form_103` | Food Bank Helpers | user-b | published |
| `form_104` | Animal Shelter Weekend | user-b | published |
| `form_105` | Marathon Water Station | user-b | closed |
| `form_999` | **does not exist**; use it to demonstrate `404 Not Found` | n/a | n/a |

New forms get IDs starting at `form_106`.

**Quick demo checklist**

| Demonstrates | Request | Expected |
|---|---|---|
| Admin sees everything | `GET /api/v1/forms` with `admin-token` | 5 forms |
| User sees only their own | `GET /api/v1/forms` with `user-a-token` | `form_101`, `form_102` |
| Access to another user's form | `GET /api/v1/forms/form_103` with `user-a-token` | `404` |
| Non-existent form | `GET /api/v1/forms/form_999` with `admin-token` | `404` |
| Missing token | `GET /api/v1/forms` with no header | `401` |
| Validation | `POST /api/v1/forms` with `{}` | `400`, four "required" errors |
| Duplicate title | `POST` "Beach Cleanup Volunteers" with `user-a-token` | `409` |
| Unsupported method | `PATCH /api/v1/forms/form_101` | `405` |
