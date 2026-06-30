"""Dashboard service: aggregates report/hotspot/prediction data for the dashboard UI."""

from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.hotspot import Hotspot
from app.models.pollution_report import PollutionReport
from app.models.prediction import Prediction
from app.services.weather_service import latest_known_aqi
from app.utils.constants import HotspotStatus


def get_dashboard_stats(db: Session) -> dict:
    """Total reports, today's reports, active hotspots, current AQI, predicted AQI."""
    total_reports = db.query(func.count(PollutionReport.id)).scalar() or 0

    today = date.today()
    todays_reports = (
        db.query(func.count(PollutionReport.id))
        .filter(func.date(PollutionReport.created_at) == today)
        .scalar()
        or 0
    )

    active_hotspots = (
        db.query(func.count(Hotspot.id)).filter(Hotspot.status == HotspotStatus.ACTIVE).scalar() or 0
    )

    current_aqi = latest_known_aqi(db)

    latest_prediction = db.query(Prediction).order_by(Prediction.created_at.desc()).first()
    predicted_aqi_next_24h = latest_prediction.predicted_aqi if latest_prediction else None

    return {
        "total_reports": total_reports,
        "todays_reports": todays_reports,
        "active_hotspots": active_hotspots,
        "current_aqi": current_aqi,
        "predicted_aqi_next_24h": predicted_aqi_next_24h,
    }


def get_reports_by_category(db: Session) -> list[dict]:
    rows = (
        db.query(PollutionReport.pollution_type, func.count(PollutionReport.id))
        .group_by(PollutionReport.pollution_type)
        .all()
    )
    return [{"category": ptype.value, "count": count} for ptype, count in rows]


def get_reports_by_severity(db: Session) -> list[dict]:
    rows = (
        db.query(PollutionReport.severity, func.count(PollutionReport.id))
        .group_by(PollutionReport.severity)
        .all()
    )
    return [{"severity": sev.value, "count": count} for sev, count in rows]


def get_pollution_trend(db: Session, days: int = 14) -> list[dict]:
    """Daily report counts (and average AQI, where sensor data exists) over the trailing window."""
    since = datetime.utcnow() - timedelta(days=days)

    report_rows = (
        db.query(func.date(PollutionReport.created_at), func.count(PollutionReport.id))
        .filter(PollutionReport.created_at >= since)
        .group_by(func.date(PollutionReport.created_at))
        .order_by(func.date(PollutionReport.created_at))
        .all()
    )

    from app.models.sensor_data import SensorData

    aqi_rows = dict(
        db.query(func.date(SensorData.timestamp), func.avg(SensorData.aqi))
        .filter(SensorData.timestamp >= since)
        .group_by(func.date(SensorData.timestamp))
        .all()
    )

    trend = []
    for day, count in report_rows:
        avg_aqi = aqi_rows.get(day)
        trend.append(
            {
                "date": day,
                "report_count": count,
                "average_aqi": round(float(avg_aqi), 1) if avg_aqi is not None else None,
            }
        )
    return trend
