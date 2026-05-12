from fastapi import APIRouter, Depends

from finhealth.presentation.dependencies import (
    ValidatedDateRange,
    get_dashboard_use_case,
    validate_date_range,
)
from finhealth.presentation.schemas.dashboard import DashboardResponse
from finhealth.use_cases.get_dashboard_summary import (
    GetDashboardSummaryUseCase,
)

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    date_range: ValidatedDateRange = Depends(validate_date_range),
    use_case: GetDashboardSummaryUseCase = Depends(get_dashboard_use_case),
) -> DashboardResponse:
    dto = await use_case.execute(date_range.from_date, date_range.to_date)
    return DashboardResponse.model_validate(dto)
