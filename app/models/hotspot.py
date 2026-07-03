"""Hotspot model: DBSCAN-derived pollution clusters with risk scoring."""

from datetime import datetime, timezone
...
datetime.now(timezone.utc)

from sqlalchemy import DateTime, Enum, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.constants import HotspotStatus


class Hotspot(Base):
    __tablename__ = "hotspots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cluster_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    status: Mapped[HotspotStatus] = mapped_column(
        Enum(HotspotStatus, name="hotspot_status"), nullable=False, default=HotspotStatus.ACTIVE
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Hotspot id={self.id} risk={self.risk_score} size={self.cluster_size}>"
