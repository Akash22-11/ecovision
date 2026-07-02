"""Map service:."""

from datetime import date

from sqlalchemy.orm import Session

from app.services.report_service import list_reports
from app.utils.constants import PollutionType, ReportStatus, SeverityLevel


def get_map_markers(
    db: Session,
    pollution_type: PollutionType | None = None,
    severity: SeverityLevel | None = None,
    status: ReportStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
  
    """
    Build map marker payloads, applying the same filters as the report list
    endpoint (type / severity / date). Color-coding by severity is left to
    the frontend, which receives the `severity` field per marker.
    """
    
    reports = list_reports(
        db,
        pollution_type=pollution_type,
        severity=severity,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=0,
        limit=2000,
    )

    return [
        {
            "id": r.id,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "pollution_type": r.pollution_type,
            "severity": r.severity,
            "status": r.status.value,
            "description": r.description,
            "image_path": r.image_path,
            "created_at": r.created_at,
        }
        for r in reports
    ]
