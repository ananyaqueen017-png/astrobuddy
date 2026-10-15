import logging
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.services.astro.errors import AstroInputError, EngineUnavailableError

log = logging.getLogger("astrobuddy")


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str, field_errors: Optional[dict] = None):
        super().__init__(message)
        self.status_code, self.code, self.message, self.field_errors = status_code, code, message, field_errors


def _body(message: str, code: str, field_errors: Optional[dict] = None) -> dict:
    body = {"message": message, "code": code}
    if field_errors:
        body["fieldErrors"] = field_errors
    return body


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app(_: Request, e: AppError):
        return JSONResponse(_body(e.message, e.code, e.field_errors), status_code=e.status_code)

    @app.exception_handler(AstroInputError)
    async def _astro(_: Request, e: AstroInputError):
        return JSONResponse(_body(e.message, "invalid_input", {e.field: e.message}), status_code=422)

    @app.exception_handler(EngineUnavailableError)
    async def _engine(_: Request, e: EngineUnavailableError):
        return JSONResponse(_body(str(e), "engine_unavailable"), status_code=503)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, e: RequestValidationError):
        fields = {}
        for err in e.errors():
            loc = [str(p) for p in err["loc"] if p not in ("body", "query")]
            key = loc[-1] if loc else "body"
            fields.setdefault(key, err["msg"])
        return JSONResponse(_body("Some fields are invalid. Check the highlighted values.",
                                  "validation_error", fields), status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, e: StarletteHTTPException):
        return JSONResponse(_body(str(e.detail), "http_error"), status_code=e.status_code)

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, e: Exception):
        log.exception("Unhandled error")
        return JSONResponse(_body("Unexpected server error.", "internal_error"), status_code=500)
