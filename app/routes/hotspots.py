"""Hotspot Detection routes: trigger clustering, list/rank hotspots, view history."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_municipality_admin
from app.models.user import User
from app.schemas.hotspot import HotspotGenerateResponse, HotspotResponse
from app.services.hotspot_service import generate_hotspots, list_hotspots
from app.utils.constants import HotspotStatus

router = APIRouter(prefix="/hotspots", tags=["Hotspot Detection"])


@router.post(
    "/generate",
    response_model=HotspotGenerateResponse,
    summary="Run DBSCAN clustering over recent reports (Municipality Admin only)",
    description="Clusters pollution reports from the last 14 days and computes a risk score per cluster.",
)
def generate(
    db: Session = Depends(get_db), _admin: User = Depends(require_municipality_admin)
) -> HotspotGenerateResponse:
    hotspots = generate_hotspots(db)
    return HotspotGenerateResponse(
        hotspots_created=len(hotspots),
        hotspots=[HotspotResponse.model_validate(h) for h in hotspots],
    )


@router.get(
    "",
    response_model=list[HotspotResponse],
    summary="List hotspots ranked by risk score",
    description="Returns hotspots (optionally filtered by status), ranked highest-risk first. "
    "Use status=active for the current map; omit it to view full history.",
)
def get_hotspots(
    status_filter: HotspotStatus | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[HotspotResponse]:
    hotspots = list_hotspots(db, status=status_filter, limit=limit)
    return [HotspotResponse.model_validate(h) for h in hotspots]
