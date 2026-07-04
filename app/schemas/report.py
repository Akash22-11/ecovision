"""Pydantic schemas for pollution report creation, responses, and filters."""

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from app.utils.constants import PollutionType, ReportStatus, SeverityLevel

class ReportCreateRequest(BaseModel):
    

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    pollution_type: PollutionType | None = Field(
        default=None,
        description="Optional citizen-selected category; AI detection may override this.",
    )
    description: str | None = Field(default=None, max_length=2000)

class DetectionResult(BaseModel):
    """AI detection result returned alongside a created report."""

    type: str
    confidence: float
    severity: SeverityLevel
    mock: bool = Field(
        default=False, description="True if no trained YOLOv8 weights were found (demo mode)."
    )


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    image_path: str
    processed_image_path: str | None
    latitude: float
    longitude: float
    address: str | None
    pollution_type: PollutionType
    confidence: float
    severity: SeverityLevel
    description: str | None
    status: ReportStatus
    created_at: datetime


class ReportUploadResponse(BaseModel):
    report: ReportResponse
    detection: DetectionResult


class ReportStatusUpdateRequest(BaseModel):
    status: ReportStatus


class ReportFilters(BaseModel):
    """Query-parameter filters shared by GET /reports and the map endpoint."""

    pollution_type: PollutionType | None = None
    severity: SeverityLevel | None = None
    status: ReportStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
