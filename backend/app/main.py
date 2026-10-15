from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.core.config import get_settings
from app.core.errors import install_error_handlers
from app.routers import ask, charts, dashas, health, lab, scaffold, transits


def create_app() -> FastAPI:
    app = FastAPI(title="AstroBuddy API", version=__version__,
                  description="Chart calculation, dashas and transits. Interpretation endpoints are optional.")
    app.add_middleware(
        CORSMiddleware, allow_origins=get_settings().cors_origin_list,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"], allow_credentials=False,
    )
    install_error_handlers(app)

    v1 = APIRouter(prefix="/api/v1")
    for r in (health.router, charts.router, dashas.router, transits.router, ask.router, lab.router,
              scaffold.router):
        v1.include_router(r)
    app.include_router(v1)
    app.include_router(health.router)  # plain /health for load balancers
    return app


app = create_app()
