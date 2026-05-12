from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from finhealth.presentation.dependencies import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    try:
        await session.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "db": "ok"},
        )
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "db": "unreachable"},
        )
