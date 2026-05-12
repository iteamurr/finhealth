from fastapi import APIRouter, Depends

from finhealth.presentation.dependencies import (
    ValidatedDateRange,
    get_alerts_use_case,
    validate_date_range,
)
from finhealth.presentation.schemas.alerts import AlertResponse
from finhealth.use_cases.get_alerts import GetAlertsUseCase

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[AlertResponse])
async def get_alerts(
    date_range: ValidatedDateRange = Depends(validate_date_range),
    use_case: GetAlertsUseCase = Depends(get_alerts_use_case),
) -> list[AlertResponse]:
    alerts = await use_case.execute(date_range.from_date, date_range.to_date)
    return [AlertResponse.model_validate(a) for a in alerts]
