"""
Request body models (Pydantic).
A model is a description of what a valid request body looks like.
FastAPI checks every incoming body against it automatically. If something
is wrong, our validation handler in errors.py turns it into a 400
VALIDATION_ERROR with one "details" entry per problem.
Note: id, ownerId, createdAt and updatedAt are NOT here on purpose.
The server sets them. Because of extra="forbid", a client that sends
them gets "This field is not allowed."
"""

from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
FormStatus = Literal["draft", "published", "closed"]
QuestionType = Literal["text", "yes_no", "number"]
_STRICT = ConfigDict(extra="forbid", str_strip_whitespace=True)

class Question(BaseModel):
    """One question a volunteer will answer, e.g. "Full name"."""
    model_config = _STRICT
    label: StrictStr = Field(min_length=1, max_length=200)
    type: QuestionType = "text"
    required: StrictBool = False

class FormCreate(BaseModel):
    """Body for POST /api/v1/forms."""
    model_config = _STRICT
    title: StrictStr = Field(min_length=3, max_length=100)
    description: StrictStr | None = Field(default=None, max_length=1000)
    location: StrictStr | None = Field(default=None, max_length=100)
    eventDate: date
    capacity: StrictInt = Field(ge=1, le=10000)
    status: FormStatus = "draft"
    questions: list[Question] = Field(min_length=1, max_length=50)


class FormUpdate(FormCreate):
    """Body for PUT /api/v1/forms/{id}.
    PUT means "replace the whole form", so it needs the same fields and the
    same rules as create. Inheriting from FormCreate keeps them identical:
    change a rule in one place and both endpoints follow.
    """