"""
Mock authentication.
There is no real login. Each request sends one of three fixed tokens:
    Authorization: Bearer user-a-token
current_user() reads that header and returns which user is calling.
"""
from fastapi import Header 
from app.errors import ApiError
 
TOKENS = {
    "user-a-token": {"id": "user-a", "name": "User A (Green Baku)", "role": "member"},
    "user-b-token": {"id": "user-b", "name": "User B (Help Ganja)", "role": "member"},
    "admin-token":  {"id": "admin",  "name": "Platform Admin",      "role": "admin"},
}
 
_AUTH_HEADER = {"WWW-Authenticate": "Bearer"}
 
def current_user(authorization: str | None = Header(default=None)) -> dict:
    """Use in a route like:  user: dict = Depends(current_user)"""
    if not authorization:
        raise ApiError(401, "UNAUTHORIZED", "Authentication token is missing. Send 'Authorization: Bearer <token>'.", headers=_AUTH_HEADER)
 
    scheme, _, token = authorization.partition(" ")
    if scheme != "Bearer" or not token:
        raise ApiError(401, "UNAUTHORIZED", "Authorization header must be in the format 'Bearer <token>'.", headers=_AUTH_HEADER)
    user = TOKENS.get(token.strip())
    if user is None:
        raise ApiError(401, "UNAUTHORIZED", "Authentication token is invalid.", headers=_AUTH_HEADER)
    return user
 
 
def is_admin(user: dict) -> bool:
    return user["role"] == "admin"
 