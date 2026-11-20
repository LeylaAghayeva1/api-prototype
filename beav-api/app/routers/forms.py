"""
HTTP routes for the "forms" resource.

Each route does three things only:
  1. FastAPI checks the token (current_user) and the body (schemas)
  2. call the matching function in forms_service
  3. wrap the result with success(...)
"""

from fastapi import APIRouter, Depends, Query

from app.auth import current_user
from app.errors import success
from app.schemas import FormCreate, FormStatus, FormUpdate
from app.services import forms_service

router = APIRouter(prefix="/api/v1/forms", tags=["Forms"])


@router.get("", summary="List forms")
def list_forms(
    page: int = Query(1, ge=1, description="Page number, starts at 1"),
    perPage: int = Query(10, ge=1, le=100, description="Forms per page (1-100)"),
    status: FormStatus | None = Query(None, description="Filter: draft, published or closed"),
    user: dict = Depends(current_user),
):
    forms, meta = forms_service.list_forms(user, page, perPage, status)
    return success(forms, f"{meta['total']} form(s) found.", meta=meta)


@router.get("/{form_id}", summary="Get one form")
def get_form(form_id: str, user: dict = Depends(current_user)):
    form = forms_service.get_form(form_id, user)
    return success(form, "Form retrieved successfully.")


@router.post("", status_code=201, summary="Create a form")
def create_form(body: FormCreate, user: dict = Depends(current_user)):
    form = forms_service.create_form(body, user)
    return success(form, "Form created successfully.", status_code=201)


@router.put("/{form_id}", summary="Update a form")
def update_form(form_id: str, body: FormUpdate, user: dict = Depends(current_user)):
    form = forms_service.update_form(form_id, body, user)
    return success(form, "Form updated successfully.")


@router.delete("/{form_id}", summary="Delete a form")
def delete_form(form_id: str, user: dict = Depends(current_user)):
    forms_service.delete_form(form_id, user)
    return success(None, "Form deleted successfully.")
