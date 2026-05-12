from fastapi import APIRouter, Depends, Query

from finhealth.presentation.dependencies import (
    ValidatedDateRange,
    get_profit_loss_use_case,
    validate_date_range,
)
from finhealth.presentation.schemas.pnl import ProfitLossResponse
from finhealth.use_cases.get_profit_loss import GetProfitLossUseCase

router = APIRouter(tags=["pnl"])


@router.get("/pnl", response_model=ProfitLossResponse)
async def get_profit_loss(
    date_range: ValidatedDateRange = Depends(validate_date_range),
    marketplace: str | None = Query(None),
    use_case: GetProfitLossUseCase = Depends(get_profit_loss_use_case),
) -> ProfitLossResponse:
    dto = await use_case.execute(
        date_range.from_date, date_range.to_date, marketplace
    )
    return ProfitLossResponse.model_validate(dto)
