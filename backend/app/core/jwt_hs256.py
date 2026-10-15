"""Minimal HS256 JWT verification (stdlib only) for Supabase's legacy shared-secret tokens.

Projects using asymmetric JWT signing keys (ES256/RS256) need JWKS verification instead;
see backend/README.md.
"""
import base64
import hashlib
import hmac
import json
import time as _time
from typing import Optional


class JWTError(Exception):
    pass


def _b64d(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def verify_hs256(token: str, secret: str, audience: Optional[str] = "authenticated",
                 now: Optional[float] = None, leeway: int = 30) -> dict:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        header = json.loads(_b64d(header_b64))
        payload = json.loads(_b64d(payload_b64))
        signature = _b64d(sig_b64)
    except Exception:
        raise JWTError("Malformed token")
    if header.get("alg") != "HS256":
        raise JWTError("Unsupported token algorithm")
    expected = hmac.new(secret.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, signature):
        raise JWTError("Invalid signature")
    current = _time.time() if now is None else now
    exp = payload.get("exp")
    if not isinstance(exp, (int, float)) or current > exp + leeway:
        raise JWTError("Token expired or missing exp")
    if audience is not None:
        aud = payload.get("aud")
        if audience not in (aud if isinstance(aud, list) else [aud]):
            raise JWTError("Wrong audience")
    if not payload.get("sub"):
        raise JWTError("Missing subject")
    return payload
