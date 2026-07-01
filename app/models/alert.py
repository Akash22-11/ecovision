"""Alert model: municipality alerts generated from high-risk hotspots."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.constants import AlertStatus


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hotspot_id: Mapped[int] = mapped_column(ForeignKey("hotspots.id", ondelete="CASCADE"), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(500), nullable=False)

    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status"), nullable=False, default=AlertStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False, index=True)

    hotspot = relationship("Hotspot")

    def __repr__(self) -> str:
        return f"<Alert id={self.id} status={self.status} hotspot_id={self.hotspot_id}>"
