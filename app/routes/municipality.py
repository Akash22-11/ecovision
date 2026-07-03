"""Municipality Alert routes: generate alerts from hotspots, view history, resolve."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_municipality_admin
from app.models.user import User
from app.schemas.alert import AlertResolveRequest, AlertResponse
from app.services.alert_service import generate_alerts_for_active_hotspots, list_alerts, resolve_alert
from app.utils.constants import AlertStatus

router = APIRouter(prefix="/municipality", tags=["Municipality Alerts"])


@router.get(
    "/alerts",
    response_model=list[AlertResponse],
    summary="List municipality alerts (Municipality Admin only)",
    description=(
        "Returns alerts generated from high-risk hotspots, each including the recommended "
        "action and current status (Sent, Pending, Resolved). Automatically generates fresh "
        "alerts for any qualifying hotspot that doesn't already have one."
    ),
)
def get_alerts(
    status_filter: AlertStatus | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_municipality_admin),
) -> list[AlertResponse]:
    generate_alerts_for_active_hotspots(db)
    alerts = list_alerts(db, status=status_filter)
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post(
    "/resolve",
    response_model=AlertResponse,
    summary="Mark an alert as resolved (Municipality Admin only)",
)
def resolve(
    payload: AlertResolveRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_municipality_admin),
) -> AlertResponse:
    alert = resolve_alert(db, payload.alert_id)
    return AlertResponse.model_validate(alert)
