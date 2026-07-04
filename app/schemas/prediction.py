"""Pydantic schemas for the AQI Prediction feature."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.utils.constants import RiskLevel

class PredictionRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_name: str | None = Field(default=None, description="Optional human-readable label")


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location: str
    latitude: float
    longitude: float
    predicted_aqi: float
    confidence_score: float
    risk_level: RiskLevel
    prediction_time: datetime
    created_at: datetime


class PredictionHistoryResponse(BaseModel):
    predictions: list[PredictionResponse]
