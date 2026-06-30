"""PollutionReport model: citizen-submitted reports with AI detection results."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.constants import PollutionType, ReportStatus, SeverityLevel


class PollutionReport(Base):
    __tablename__ = "pollution_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    processed_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    pollution_type: Mapped[PollutionType] = mapped_column(
        Enum(PollutionType, name="pollution_type"), nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    severity: Mapped[SeverityLevel] = mapped_column(
        Enum(SeverityLevel, name="severity_level"), nullable=False, default=SeverityLevel.LOW
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status"), nullable=False, default=ReportStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    reporter = relationship("User", back_populates="reports")

    def __repr__(self) -> str:
        return f"<PollutionReport id={self.id} type={self.pollution_type} severity={self.severity}>"
