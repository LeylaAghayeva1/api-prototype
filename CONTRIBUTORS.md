# Contributors

**Project:** beav, volunteer registration platform
**Course:** CSCI 3509 Intro to Software Engineering, Fall 2026, ADA University
**Team:** Team 14
**Assignment:** Assignment 2: API Prototype with Mocked Backend

| Name | Student ID | GitHub account | Responsibilities |
|---|---|---|---|
| Nuray Aghayeva | `23796` | [@NurayAghayeva](https://github.com/NurayAghayeva) | Response envelope and centralized error handling (`errors.py`); application setup (`main.py`); forms service with ownership rules (`services/forms_service.py`); CRUD routes for forms with pagination and status filter (`routers/forms.py`) |
| Leyla Aghayeva | `17752` | [@LeylaAghayeva1](https://github.com/LeylaAghayeva1) | Project structure; mock data (`data.py`); bearer token authentication (`auth.py`); request validation schemas (`schemas.py`); 409 duplicate-title check; HTML greeting page (`routers/greeting.py`); Postman collection; repository cleanup (`.gitignore`) |

## Shared work

Both members worked together on:

- Designing the API contract: choosing `forms` as the main resource, field names, error codes, and the 404-instead-of-403 decision
- API documentation (`beav-api/docs/API.md`) and `README.md`
- Testing every endpoint and error case in Postman
- The demo video
