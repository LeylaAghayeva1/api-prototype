"""
Response envelope helpers and error handlers.

Every JSON response from the API goes through this file, so all responses
have the same shape:

  success -> {"success": true,  "message": "...", "data": ..., "meta": ...}
  error   -> {"success": false, "error": {"code": "...", "message": "...", "details": [...]}}
"""

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("beav")

class ApiError(Exception):

    def __init__(self, status_code: int, code: str, message: str,
                 details: list | None = None, headers: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.headers = headers


def success(data, message: str, status_code: int = 200, meta: dict | None = None) -> JSONResponse:
    body = {"success": True, "message": message, "data": data}
    if meta is not None:
        body["meta"] = meta
    return JSONResponse(status_code=status_code, content=jsonable_encoder(body))


def error_response(status_code: int, code: str, message: str,
                   details: list | None = None, headers: dict | None = None) -> JSONResponse:
    error = {"code": code, "message": message}
    if details:
        error["details"] = details
    return JSONResponse(status_code=status_code,
                        content={"success": False, "error": error},
                        headers=headers)

async def api_error_handler(request: Request, exc: ApiError):
    return error_response(exc.status_code, exc.code, exc.message, exc.details, exc.headers)


def _readable_message(err: dict) -> str:
    if err["type"] == "missing":
        return "This field is required."
    if err["type"] == "extra_forbidden":
        return "This field is not allowed."
    if err["type"] == "json_invalid":
        return "The request body is not valid JSON."
    return err["msg"]


async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        location = [str(part) for part in err["loc"][1:]]
        if err["type"] == "json_invalid" or not location:
            field = "body"
        else:
            field = ".".join(location)
        details.append({"field": field, "message": _readable_message(err)})

    return error_response(400, "VALIDATION_ERROR",
                          "The request contains invalid or missing fields.", details)

_HTTP_ERRORS = {
    404: ("NOT_FOUND", "The requested resource was not found."),
    405: ("METHOD_NOT_ALLOWED", "This HTTP method is not supported for this endpoint."),
}


async def http_error_handler(request: Request, exc: StarletteHTTPException):
    code, message = _HTTP_ERRORS.get(exc.status_code, ("HTTP_ERROR", str(exc.detail)))
    return error_response(exc.status_code, code, message, headers=exc.headers)


async def unexpected_error_handler(request: Request, exc: Exception):
    logger.exception("Unexpected error on %s %s", request.method, request.url.path)
    return error_response(500, "INTERNAL_ERROR", "Something went wrong on the server. Please try again later.")

def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
