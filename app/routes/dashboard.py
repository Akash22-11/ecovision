from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardChartsResponse, DashboardMapResponse, DashboardStatsResponse
from app.services.dashboard_service import (
    get_dashboard_stats,
    get_pollution_trend,
    get_reports_by_category,
    get_reports_by_severity,
)
from app.services.map_service import get_map_markers
from app.utils.constants import PollutionType, ReportStatus, SeverityLevel

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
    summary="Top-line dashboard stats",
    description="Total reports, today's reports, active hotspots, current AQI, predicted AQI.",
)
def stats(db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)) -> DashboardStatsResponse:
    return DashboardStatsResponse(**get_dashboard_stats(db))


@router.get(
    "/charts",
    response_model=DashboardChartsResponse,
    summary="Chart data: reports by category/severity and pollution trend",
)
def charts(
    trend_days: int = 14,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> DashboardChartsResponse:
    return DashboardChartsResponse(
        reports_by_category=get_reports_by_category(db),
        reports_by_severity=get_reports_by_severity(db),
        pollution_trend=get_pollution_trend(db, days=trend_days),
    )


@router.get(
    "/map",
    response_model=DashboardMapResponse,
    summary="Interactive pollution map data",
    description=(
        "Returns color-codeable markers for every report matching the given filters "
        "(pollution type, severity, status, date range), for rendering on the map UI."
    ),
)
def map_data(
    pollution_type: PollutionType | None = None,
    severity: SeverityLevel | None = None,
    status_filter: ReportStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> DashboardMapResponse:
    markers = get_map_markers(
        db,
        pollution_type=pollution_type,
        severity=severity,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
    )
    return DashboardMapResponse(markers=markers, total=len(markers))
