"""General-purpose helper functions shared across services and the AI layer."""

import math
import uuid
from datetime import datetime, timezone

from app.utils.constants import (
    AQI_RISK_BANDS,
    EARTH_RADIUS_KM,
    SEVERITY_CONFIDENCE_THRESHOLDS,
    RiskLevel,
    SeverityLevel,
)


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def severity_from_confidence(confidence: float) -> SeverityLevel:
    """Map a YOLO detection confidence (0-1) to a SeverityLevel bucket."""
    if confidence >= SEVERITY_CONFIDENCE_THRESHOLDS[SeverityLevel.HIGH]:
        return SeverityLevel.HIGH
    if confidence >= SEVERITY_CONFIDENCE_THRESHOLDS[SeverityLevel.MEDIUM]:
        return SeverityLevel.MEDIUM
    return SeverityLevel.LOW


def risk_level_from_aqi(aqi: float) -> RiskLevel:
    """Map a numeric AQI value to a RiskLevel bucket using AQI_RISK_BANDS."""
    for low, high, level in AQI_RISK_BANDS:
        if low <= aqi <= high:
            return level
    return RiskLevel.SEVERE if aqi > AQI_RISK_BANDS[-1][1] else RiskLevel.LOW


def generate_unique_filename(original_filename: str) -> str:
    """Generate a collision-safe filename, preserving the original extension."""
    extension = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "jpg"
    timestamp = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{uuid.uuid4().hex[:10]}.{extension}"


def cluster_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
    """Simple arithmetic centroid of a list of (lat, lon) points."""
    if not points:
        raise ValueError("Cannot compute centroid of an empty point list.")
    lat = sum(p[0] for p in points) / len(points)
    lon = sum(p[1] for p in points) / len(points)
    return lat, lon
