from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.ai.hotspot_detector import HotspotCluster, ReportPoint, detect_hotspots
from app.models.hotspot import Hotspot
from app.models.pollution_report import PollutionReport
from app.utils.constants import HotspotStatus
from app.utils.logger import logger

DEFAULT_LOOKBACK_DAYS = 14


def generate_hotspots(db: Session, lookback_days: int = DEFAULT_LOOKBACK_DAYS) -> list[Hotspot]:
   
    since = datetime.utcnow() - timedelta(days=lookback_days)
    reports = (
        db.query(PollutionReport).filter(PollutionReport.created_at >= since).all()
    )

    points = [
        ReportPoint(
            report_id=r.id,
            latitude=r.latitude,
            longitude=r.longitude,
            severity=r.severity,
            confidence=r.confidence,
        )
        for r in reports
    ]

    clusters: list[HotspotCluster] = detect_hotspots(points)

    db.query(Hotspot).filter(Hotspot.status == HotspotStatus.ACTIVE).update(
        {Hotspot.status: HotspotStatus.RESOLVED}
    )

    created: list[Hotspot] = []
    report_by_id = {r.id: r for r in reports}

    for cluster in clusters:
        hotspot = Hotspot(
            latitude=cluster.latitude,
            longitude=cluster.longitude,
            risk_score=cluster.risk_score,
            cluster_size=cluster.cluster_size,
            status=HotspotStatus.ACTIVE,
        )
        db.add(hotspot)
        db.flush()                                            # assign hotspot.id without committing yet
        created.append(hotspot)

      
        dominant_type = Counter(
            report_by_id[rid].pollution_type for rid in cluster.member_report_ids if rid in report_by_id
        ).most_common(1)
        hotspot._dominant_pollution_type = dominant_type[0][0] if dominant_type else None  # type: ignore[attr-defined]

    db.commit()
    for h in created:
        db.refresh(h)

    logger.info(f"Generated {len(created)} hotspot(s) from {len(reports)} reports in last {lookback_days}d.")
    return created


def list_hotspots(db: Session, status: HotspotStatus | None = None, limit: int = 100) -> list[Hotspot]:
    query = db.query(Hotspot)
    if status:
        query = query.filter(Hotspot.status == status)
    return query.order_by(Hotspot.risk_score.desc()).limit(limit).all()
