"""
Shared enums and constant values used across the EcoVision AI backend.

Keeping these centralized avoids "magic string" drift between models,
schemas, services and the AI layer.
"""

from enum import Enum


class UserRole(str, Enum):
    """Application roles. Controls access via role-based dependencies."""

    CITIZEN = "citizen"
    MUNICIPALITY_ADMIN = "municipality_admin"


class PollutionType(str, Enum):
    """Pollution categories detected by the YOLOv8 model / selected by users."""

    SMOKE = "smoke"
    DUST = "dust"
    GARBAGE_BURNING = "garbage_burning"
    CONSTRUCTION_DUST = "construction_dust"
    INDUSTRIAL_SMOKE = "industrial_smoke"
    OTHER = "other"


class SeverityLevel(str, Enum):
    """Severity bucket derived from AI confidence score and/or AQI context."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReportStatus(str, Enum):
    """Lifecycle state of a citizen-submitted pollution report."""

    PENDING = "pending"
    VERIFIED = "verified"
    RESOLVED = "resolved"


class HotspotStatus(str, Enum):
    """Lifecycle state of a detected pollution hotspot."""

    ACTIVE = "active"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


class AlertStatus(str, Enum):
    """Lifecycle state of a municipality alert."""

    SENT = "sent"
    PENDING = "pending"
    RESOLVED = "resolved"


class RiskLevel(str, Enum):
    """Risk level used by AQI prediction and hotspot ranking."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


# --- AI / confidence thresholds -------------------------------------------------

SEVERITY_CONFIDENCE_THRESHOLDS = {
    SeverityLevel.HIGH: 0.80,
    SeverityLevel.MEDIUM: 0.55,
}
"""Confidence (0-1) at or above which a detection is classified at that severity.
Anything below the MEDIUM threshold falls back to LOW."""

# Classes the custom-trained YOLOv8 pollution model is expected to expose.
# NOTE: stock YOLOv8 (COCO weights) does NOT contain these classes - a model
# fine-tuned on a pollution dataset must be supplied via MODEL_PATH. See
# app/ai/yolo_detector.py for the graceful fallback behaviour when no
# custom weights are present.
YOLO_POLLUTION_CLASSES = [
    PollutionType.SMOKE.value,
    PollutionType.DUST.value,
    PollutionType.GARBAGE_BURNING.value,
    PollutionType.CONSTRUCTION_DUST.value,
    PollutionType.INDUSTRIAL_SMOKE.value,
]

# --- AQI bands (Indian CPCB-style buckets, used for risk_level mapping) ---------

AQI_RISK_BANDS = [
    (0, 50, RiskLevel.LOW),
    (51, 100, RiskLevel.LOW),
    (101, 200, RiskLevel.MODERATE),
    (201, 300, RiskLevel.HIGH),
    (301, 400, RiskLevel.HIGH),
    (401, 500, RiskLevel.SEVERE),
]

AQI_PUBLIC_HEALTH_WARNING_THRESHOLD = 200

# --- Hotspot detection ------------------------------------------------------------

HOTSPOT_DBSCAN_EPS_KM = 0.5          # neighborhood radius in kilometers
HOTSPOT_DBSCAN_MIN_SAMPLES = 3       # minimum reports to form a cluster
EARTH_RADIUS_KM = 6371.0088

# --- Uploads -----------------------------------------------------------------------

ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
UPLOAD_ORIGINAL_DIR = "app/uploads/original"
UPLOAD_PROCESSED_DIR = "app/uploads/processed"
