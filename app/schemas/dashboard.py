"""Pydantic schemas for the Dashboard and Interactive Pollution Map features."""

from datetime import date, datetime

from pydantic import BaseModel

from app.utils.constants import PollutionType, SeverityLevel


class DashboardStatsResponse(BaseModel):
    total_reports: int
    todays_reports: int
    active_hotspots: int
    current_aqi: float | None
    predicted_aqi_next_24h: float | None


class CategoryCount(BaseModel):
    category: str
    count: int


class SeverityCount(BaseModel):
    severity: str
    count: int


class TrendPoint(BaseModel):
    date: date
    report_count: int
    average_aqi: float | None = None


class DashboardChartsResponse(BaseModel):
    reports_by_category: list[CategoryCount]
    reports_by_severity: list[SeverityCount]
    pollution_trend: list[TrendPoint]


class MapMarker(BaseModel):
    id: int
    latitude: float
    longitude: float
    pollution_type: PollutionType
    severity: SeverityLevel
    status: str
    description: str | None
    image_path: str
    created_at: datetime


class DashboardMapResponse(BaseModel):
    markers: list[MapMarker]
    total: int
