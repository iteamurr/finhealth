from fastapi import APIRouter, Depends

from finhealth.presentation.dependencies import (
    ValidatedDateRange,
    get_cashflow_use_case,
    validate_date_range,
)
from finhealth.presentation.schemas.cashflow import CashFlowResponse
from finhealth.use_cases.get_cashflow import GetCashFlowUseCase

router = APIRouter(tags=["cashflow"])


@router.get("/cashflow", response_model=CashFlowResponse)
async def get_cashflow(
    date_range: ValidatedDateRange = Depends(validate_date_range),
    use_case: GetCashFlowUseCase = Depends(get_cashflow_use_case),
) -> CashFlowResponse:
    dto = await use_case.execute(date_range.from_date, date_range.to_date)
    return CashFlowResponse.model_validate(dto)
