"""
Report service: orchestrates the full pollution-report pipeline -
save image -> run YOLO detection -> save annotated image -> persist report.
"""

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.image_preprocessing import draw_detections, load_image, save_image
from app.ai.yolo_detector import detect_pollution
from app.models.pollution_report import PollutionReport
from app.models.user import User
from app.schemas.report import ReportCreateRequest
from app.services.upload_service import processed_image_path_for
from app.utils.constants import PollutionType, ReportStatus, SeverityLevel
from app.utils.logger import logger
from app.utils.validators import ValidationError, validate_coordinates


def create_report_with_detection(
    db: Session, user: User, payload: ReportCreateRequest, image_path: str
) -> tuple[PollutionReport, dict]:
   
    """
    Run AI detection on the uploaded image, save an annotated copy, and
    persist the resulting PollutionReport.

    Returns:
        (PollutionReport, detection_result_dict)
    """
    
    validate_coordinates(payload.latitude, payload.longitude)

    detection = detect_pollution(image_path)

    processed_path: str | None = None
    if detection["boxes"]:
        try:
            image = load_image(image_path)
            annotated = draw_detections(
                image, detection["boxes"], detection["labels"], detection["confidences"]
            )
            processed_path = processed_image_path_for(image_path)
            save_image(annotated, processed_path)
        except Exception as exc: 
            logger.error(f"Could not save annotated image for {image_path}: {exc}")
            processed_path = None


    try:
        pollution_type = PollutionType(detection["type"])
    except ValueError:
        pollution_type = payload.pollution_type or PollutionType.OTHER

    report = PollutionReport(
        user_id=user.id,
        image_path=image_path,
        processed_image_path=processed_path,
        latitude=payload.latitude,
        longitude=payload.longitude,
        pollution_type=pollution_type,
        confidence=detection["confidence"],
        severity=detection["severity"],
        description=payload.description,
        status=ReportStatus.PENDING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    logger.info(
        f"Created report #{report.id} by user {user.id}: "
        f"{pollution_type.value} ({detection['confidence']:.2f} confidence, mock={detection['mock']})"
    )
    return report, detection


def get_report_or_404(db: Session, report_id: int) -> PollutionReport:
    report = db.query(PollutionReport).filter(PollutionReport.id == report_id).first()
    if not report:
        raise ValidationError(f"Report {report_id} not found.", status_code=404)
    return report


def list_reports(
    db: Session,
    pollution_type: PollutionType | None = None,
    severity: SeverityLevel | None = None,
    status: ReportStatus | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[PollutionReport]:
    """List reports with optional filters - backs both GET /reports and the map endpoint."""
    query = db.query(PollutionReport)

    if pollution_type:
        query = query.filter(PollutionReport.pollution_type == pollution_type)
    if severity:
        query = query.filter(PollutionReport.severity == severity)
    if status:
        query = query.filter(PollutionReport.status == status)
    if start_date:
        query = query.filter(func.date(PollutionReport.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(PollutionReport.created_at) <= end_date)

    return (
        query.order_by(PollutionReport.created_at.desc()).offset(skip).limit(limit).all()
    )


def delete_report(db: Session, report_id: int, requesting_user: User) -> None:
    """Delete a report. Citizens may only delete their own reports; admins may delete any."""
    report = get_report_or_404(db, report_id)

    is_owner = report.user_id == requesting_user.id
    is_admin = requesting_user.role.value == "municipality_admin"
    if not (is_owner or is_admin):
        raise ValidationError("You do not have permission to delete this report.", status_code=403)

    db.delete(report)
    db.commit()
    logger.info(f"Deleted report #{report_id} by user {requesting_user.id}")


def update_report_status(db: Session, report_id: int, new_status: ReportStatus) -> PollutionReport:
    report = get_report_or_404(db, report_id)
    report.status = new_status
    db.commit()
    db.refresh(report)
    logger.info(f"Report #{report_id} status updated to {new_status.value}")
    return report
