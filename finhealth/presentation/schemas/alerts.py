from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alert_type: str
    severity: str
    message: str
    sku_id: str | None = None
    value: float | None = None
