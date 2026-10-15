"""Real authentication path (Supabase JWT). Inactive until SUPABASE_JWT_SECRET is configured."""
from typing import Optional

from fastapi import Depends, Header

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.jwt_hs256 import JWTError, verify_hs256


def require_user_id(authorization: Optional[str] = Header(default=None),
                    settings: Settings = Depends(get_settings)) -> str:
    if not settings.supabase_jwt_secret:
        raise AppError(503, "auth_not_configured",
                       "Authentication is not configured on this server (set SUPABASE_JWT_SECRET).")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError(401, "unauthorized", "Missing bearer token.")
    try:
        claims = verify_hs256(authorization[7:].strip(), settings.supabase_jwt_secret,
                              settings.supabase_jwt_audience)
    except JWTError:
        raise AppError(401, "unauthorized", "Invalid or expired token.")
    return claims["sub"]
