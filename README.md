# beav API: Prototype with Mocked Backend

beav is a volunteer registration platform. Organizations create registration forms, collect volunteer applications and see participation analytics; volunteers discover opportunities and join community groups.

This repository is the **first API prototype** (CSCI 3509, Assignment 2). It implements the main resource, **volunteer registration forms**, as a REST API with:

- full CRUD for `/api/v1/forms`
- token-based authentication with three mock users and role-based access (users manage only their own forms; the admin manages all)
- validation with clear, structured error responses
- an HTML greeting page at `/api/v1/greeting`

Data is **mocked in memory**. There is no database yet.

> ⚠️ **The mock data resets every time the server restarts.** Forms you create, update or delete are lost when you stop the server.

---

## Tech stack

| Part | Technology |
|---|---|
| Language | Python 3.10+ |
| Framework | FastAPI |
| Server | Uvicorn |
| Validation | Pydantic |
| Data | In-memory Python dictionary (`app/data.py`) |
| API testing | Postman |

---

## Installation and running

**Requirements:** Python **3.10 or newer** (check with `python3 --version`) and Git.

```bash
# 1. Clone the repository
git clone https://github.com/LeylaAghayeva1/api-prototype.git
cd api-prototype

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server (run from inside beav-api/)
cd beav-api
uvicorn app.main:app --reload
```

The API is now running at **http://127.0.0.1:8000**.

| Open in browser | What you see |
|---|---|
| http://127.0.0.1:8000/api/v1/greeting | HTML greeting page: project, team, endpoints |
| http://127.0.0.1:8000/docs | Interactive Swagger docs: try every endpoint in the browser |

To stop the server, press `Ctrl + C`.

---

## Authentication

Send one of these tokens in the `Authorization` header of every `/api/v1/forms` request:

```http
Authorization: Bearer user-a-token
```

| Token | User | Can do |
|---|---|---|
| `user-a-token` | User A | Manage only their own forms |
| `user-b-token` | User B | Manage only their own forms |
| `admin-token` | Platform admin | Manage all forms |

A missing or invalid token returns `401 Unauthorized`. A user who asks for another user's form gets `404 Not Found` instead of `403`, so other organizations' forms stay completely hidden. The full reasoning is in the [API documentation](beav-api/docs/API.md#2-authorization-rules).

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/greeting` | HTML greeting page (no token needed) |
| `GET` | `/api/v1/forms` | List forms; supports `page`, `perPage`, `status` |
| `GET` | `/api/v1/forms/{form_id}` | Get one form |
| `POST` | `/api/v1/forms` | Create a form |
| `PUT` | `/api/v1/forms/{form_id}` | Update (replace) a form |
| `DELETE` | `/api/v1/forms/{form_id}` | Delete a form |

📄 **Full documentation:** headers, parameters, validation rules, every success and error response, and examples are in **[`beav-api/docs/API.md`](beav-api/docs/API.md)**.

---

## Mock data

| ID | Title | Owner | Status |
|---|---|---|---|
| `form_101` | Beach Cleanup Volunteers | user-a | published |
| `form_102` | Tree Planting Day | user-a | draft |
| `form_103` | Food Bank Helpers | user-b | published |
| `form_104` | Animal Shelter Weekend | user-b | published |
| `form_105` | Marathon Water Station | user-b | closed |
| `form_999` | does not exist (use it to demo `404`) | n/a | n/a |

---

## Example requests

**List your forms**
```bash
curl -H "Authorization: Bearer user-a-token" http://127.0.0.1:8000/api/v1/forms
```

**Create a form**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/forms \
  -H "Authorization: Bearer user-a-token" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Park Cleanup Day",
        "eventDate": "2026-12-20",
        "capacity": 30,
        "status": "published",
        "questions": [{ "label": "Full name", "type": "text", "required": true }]
      }'
```

**Try to read another user's form (returns 404)**
```bash
curl -H "Authorization: Bearer user-a-token" http://127.0.0.1:8000/api/v1/forms/form_103
```

### Postman collection

The file **[`beav-api/postman_collection.json`](beav-api/postman_collection.json)** contains **37 requests** covering every success and error case, grouped in folders:

1. Greeting page
2. Successful CRUD (user and admin)
3. Authentication errors (401)
4. Authorization errors: other user's form (404)
5. Validation errors (400)
6. Other errors: 404, 405, 409

**How to use it:** Postman → **Import** → choose the file. Start the server, then click **Run collection**. Every request has a built-in test that checks the status code, the `success` field and the error code. Tokens are stored as collection variables, and the collection deletes the forms it creates, so it can be run repeatedly without restarting the server.

---

## Project structure

```
api-prototype/
├── requirements.txt
├── README.md
├── CONTRIBUTORS.md
└── beav-api/
    ├── app/
    │   ├── main.py              # creates the app, registers error handlers and routers
    │   ├── errors.py            # ApiError, success/error envelope, error handlers
    │   ├── auth.py              # mock tokens and current_user check
    │   ├── data.py              # in-memory mock forms (resets on restart)
    │   ├── schemas.py           # Pydantic validation models
    │   ├── services/
    │   │   └── forms_service.py # business rules: ownership, 404, 409
    │   └── routers/
    │       ├── forms.py         # CRUD routes for /api/v1/forms
    │       └── greeting.py      # HTML greeting page
    ├── docs/
    │   └── API.md               # full API documentation
    └── postman_collection.json
```

**How a request flows:** `routers/` handles HTTP only (reads the request, returns the response) → `services/` decides what happens (who may access what, duplicate titles) → `data.py` stores the forms. `errors.py` makes sure every response, success or error, has the same envelope.

---

## Demo video

▶️ **YouTube:** https://youtu.be/2qDWi3TM7LE?si=pAiETQI6ad1O9n4a

The video shows successful CRUD operations, authorization failures, validation errors, and the HTML greeting page.

---

## Team and contributions

| Member | Student ID | Worked on |
|---|---|---|
| **Nuray Aghayeva** | `23796` | Centralized error handling and response envelope; app setup; forms service with ownership rules; CRUD routes with pagination and status filter |
| **Leyla Aghayeva** | `17752` | Project structure; mock data; token authentication; validation schemas; duplicate-title (409) check; HTML greeting page; Postman collection; repository cleanup |
| **Both** | | API design decisions, API documentation, README, testing, demo video |

See [`CONTRIBUTORS.md`](CONTRIBUTORS.md) for details.

### Commit summary

Output of `git shortlog -sn --all`:

```
     9	LeylaAghayeva1
     5	NurayAghayeva
     2	Nuray
```

> `NurayAghayeva` and `Nuray` are the same person (same email, `aghayevnuray@gmail.com`). Her local Git name was set to "Nuray" for her first commits.
