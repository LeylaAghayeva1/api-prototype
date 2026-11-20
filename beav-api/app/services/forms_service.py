"""
Business rules for forms.

The router (routers/forms.py) only handles HTTP: it reads the request and
sends the response. All the decisions live here:
  - who is allowed to see which forms
  - what happens when a form does not exist
  - how a form is created, updated and deleted
"""

from datetime import datetime, timezone

from app.auth import is_admin
from app.data import FORMS, next_form_id
from app.errors import ApiError
from app.schemas import FormCreate, FormUpdate


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _can_access(user: dict, form: dict) -> bool:
    return is_admin(user) or form["ownerId"] == user["id"]


def _get_accessible_form(form_id: str, user: dict) -> dict:
    """Find a form the user is allowed to access, or stop with 404.

    We return 404 (not 403) when the form belongs to someone else.
    A 403 would tell the caller "this form exists, you just can't see it".
    A 404 reveals nothing, which protects other organizations' data (FR-14).
    """
    form = FORMS.get(form_id)
    if form is None or not _can_access(user, form):
        raise ApiError(404, "NOT_FOUND", f"Form with id '{form_id}' was not found.")
    return form


def list_forms(user: dict, page: int, per_page: int, status: str | None) -> tuple[list, dict]:
    forms = [f for f in FORMS.values() if _can_access(user, f)]

    if status is not None:
        forms = [f for f in forms if f["status"] == status]

    total = len(forms)
    start = (page - 1) * per_page
    page_items = forms[start:start + per_page]

    meta = {"total": total, "page": page, "perPage": per_page}
    return page_items, meta


def get_form(form_id: str, user: dict) -> dict:
    return _get_accessible_form(form_id, user)


def create_form(body: FormCreate, user: dict) -> dict:
    now = _now()
    form = {
        "id": next_form_id(),
        **body.model_dump(mode="json"),
        "ownerId": user["id"],
        "createdAt": now,
        "updatedAt": now,
    }
    FORMS[form["id"]] = form
    return form


def update_form(form_id: str, body: FormUpdate, user: dict) -> dict:
    form = _get_accessible_form(form_id, user)
    form.update(body.model_dump(mode="json"))
    form["updatedAt"] = _now()
    return form


def delete_form(form_id: str, user: dict) -> None:
    _get_accessible_form(form_id, user)
    del FORMS[form_id]
