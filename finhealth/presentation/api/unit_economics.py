from fastapi import APIRouter, Depends

from finhealth.presentation.dependencies import (
    ValidatedDateRange,
    get_unit_economics_use_case,
    validate_date_range,
)
from finhealth.presentation.schemas.sku import SKUProfitResponse
from finhealth.use_cases.get_unit_economics import GetUnitEconomicsUseCase

router = APIRouter(tags=["unit-economics"])


@router.get("/unit-economics", response_model=list[SKUProfitResponse])
async def get_unit_economics(
    date_range: ValidatedDateRange = Depends(validate_date_range),
    use_case: GetUnitEconomicsUseCase = Depends(get_unit_economics_use_case),
) -> list[SKUProfitResponse]:
    profits = await use_case.execute(date_range.from_date, date_range.to_date)
    return [SKUProfitResponse.model_validate(p) for p in profits]
