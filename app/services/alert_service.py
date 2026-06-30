"""Alert service: generates municipality alerts from high-risk hotspots and tracks resolution."""

from sqlalchemy.orm import Session

from app.ai.recommendation_engine import recommend_action
from app.models.alert import Alert
from app.models.hotspot import Hotspot
from app.services.weather_service import latest_known_aqi
from app.utils.constants import AlertStatus, HotspotStatus, PollutionType
from app.utils.logger import logger
from app.utils.validators import ValidationError

HIGH_RISK_THRESHOLD = 60.0  # risk_score (0-100) at/above which an alert is generated


def generate_alerts_for_active_hotspots(db: Session) -> list[Alert]:
    """
    For every ACTIVE hotspot above HIGH_RISK_THRESHOLD that doesn't already
    have a pending/sent alert, create one using the recommendation engine.
    """
    high_risk_hotspots = (
        db.query(Hotspot)
        .filter(Hotspot.status == HotspotStatus.ACTIVE, Hotspot.risk_score >= HIGH_RISK_THRESHOLD)
        .all()
    )

    current_aqi = latest_known_aqi(db)
    created: list[Alert] = []

    for hotspot in high_risk_hotspots:
        already_alerted = (
            db.query(Alert)
            .filter(Alert.hotspot_id == hotspot.id, Alert.status != AlertStatus.RESOLVED)
            .first()
        )
        if already_alerted:
            continue

        dominant_type = getattr(hotspot, "_dominant_pollution_type", None) or PollutionType.OTHER
        recommendation = recommend_action(
            dominant_pollution_type=dominant_type,
            risk_score=hotspot.risk_score,
            cluster_size=hotspot.cluster_size,
            current_aqi=current_aqi,
        )

        alert = Alert(
            hotspot_id=hotspot.id,
            message=recommendation.message,
            recommended_action=recommendation.recommended_action,
            status=AlertStatus.SENT,
        )
        db.add(alert)
        created.append(alert)

    db.commit()
    for a in created:
        db.refresh(a)

    logger.info(f"Generated {len(created)} municipality alert(s) from {len(high_risk_hotspots)} high-risk hotspots.")
    return created


def list_alerts(db: Session, status: AlertStatus | None = None, limit: int = 100) -> list[Alert]:
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.created_at.desc()).limit(limit).all()


def resolve_alert(db: Session, alert_id: int) -> Alert:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise ValidationError(f"Alert {alert_id} not found.", status_code=404)

    alert.status = AlertStatus.RESOLVED
    db.commit()
    db.refresh(alert)
    logger.info(f"Resolved alert #{alert_id}")
    return alert
