from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.utils.constants import AlertStatus


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotspot_id: int
    message: str
    recommended_action: str
    status: AlertStatus
    created_at: datetime


class AlertResolveRequest(BaseModel):
    alert_id: int


class HighRiskLocationResponse(BaseModel):
    hotspot_id: int
    latitude: float
    longitude: float
    risk_score: float
    risk_level: str
    recommended_action: str
