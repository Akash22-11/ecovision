"""Pydantic schemas for hotspot detection and history."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.utils.constants import HotspotStatus

class HotspotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    latitude: float
    longitude: float
    risk_score: float
    cluster_size: int
    status: HotspotStatus
    created_at: datetime


class HotspotGenerateResponse(BaseModel):
    hotspots_created: int
    hotspots: list[HotspotResponse]
