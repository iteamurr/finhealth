from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from finhealth.domain.exceptions import DomainException
from finhealth.presentation.api import (
    alerts,
    cashflow,
    dashboard,
    health,
    pnl,
    unit_economics,
)


def create_app() -> FastAPI:
    app = FastAPI(title="FinHealth SMB", version="0.1.0")

    @app.get("/health")
    async def root_health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request, exc: DomainException
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(dashboard.router, prefix="/api/v1")
    app.include_router(pnl.router, prefix="/api/v1")
    app.include_router(unit_economics.router, prefix="/api/v1")
    app.include_router(cashflow.router, prefix="/api/v1")
    app.include_router(alerts.router, prefix="/api/v1")

    return app


app = create_app()
