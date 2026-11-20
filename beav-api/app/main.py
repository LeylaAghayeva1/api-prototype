""" NurayAghayeva worked on this file"""

"""
Entry point of the beav API.

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.errors import register_error_handlers
from app.routers import forms

app = FastAPI(
    title="beav API",
    version="1.0.0",
    description="Prototype API for beav, a volunteer registration platform. "
                "Uses mocked in-memory data that resets on every restart.",
)

register_error_handlers(app)

app.include_router(forms.router)
