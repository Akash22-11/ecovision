"""Pollution report routes: upload (with AI detection), list, retrieve, status update, delete."""

from datetime import date

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_municipality_admin
from app.models.user import User
from app.schemas.report import (
    ReportCreateRequest,
    ReportResponse,
    ReportStatusUpdateRequest,
    ReportUploadResponse,
)
from app.services.report_service import (
    create_report_with_detection,
    delete_report,
    get_report_or_404,
    list_reports,
    update_report_status,
)
from app.services.upload_service import save_uploaded_image
from app.utils.constants import PollutionType, ReportStatus, SeverityLevel

router = APIRouter(prefix="/reports", tags=["Pollution Reports"])


@router.post(
    "/upload",
    response_model=ReportUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a pollution report image",
    description=(
        "Citizens upload a photo with GPS coordinates and an optional description. "
        "The image is run through the YOLOv8 pollution detector automatically; "
        "the resulting type/confidence/severity are stored on the report."
    ),
)
async def upload_report(
    image: UploadFile = File(..., description="JPEG/PNG/WEBP photo of the pollution incident"),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    pollution_type: PollutionType | None = Form(default=None),
    description: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportUploadResponse:
    payload = ReportCreateRequest(
        latitude=latitude, longitude=longitude, pollution_type=pollution_type, description=description
    )
    saved_path = await save_uploaded_image(image)
    report, detection = create_report_with_detection(db, current_user, payload, saved_path)

    return ReportUploadResponse(
        report=ReportResponse.model_validate(report),
        detection={
            "type": detection["type"],
            "confidence": round(detection["confidence"] * 100, 1),
            "severity": detection["severity"],
            "mock": detection["mock"],
        },
    )


@router.get(
    "",
    response_model=list[ReportResponse],
    summary="List pollution reports",
    description="Supports filtering by pollution type, severity, status, and date range.",
)
def get_reports(
    pollution_type: PollutionType | None = None,
    severity: SeverityLevel | None = None,
    status_filter: ReportStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[ReportResponse]:
    reports = list_reports(
        db,
        pollution_type=pollution_type,
        severity=severity,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return [ReportResponse.model_validate(r) for r in reports]


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get a single pollution report by ID",
)
def get_report(
    report_id: int, db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)
) -> ReportResponse:
    report = get_report_or_404(db, report_id)
    return ReportResponse.model_validate(report)


@router.patch(
    "/{report_id}/status",
    response_model=ReportResponse,
    summary="Update a report's status (Municipality Admin only)",
    description="Transitions a report between Pending, Verified, and Resolved.",
)
def patch_report_status(
    report_id: int,
    payload: ReportStatusUpdateRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_municipality_admin),
) -> ReportResponse:
    report = update_report_status(db, report_id, payload.status)
    return ReportResponse.model_validate(report)


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pollution report",
    description="Citizens may delete their own reports; municipality admins may delete any report.",
)
def remove_report(
    report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    delete_report(db, report_id, current_user)
