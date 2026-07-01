"""
Hotspot detection using DBSCAN clustering over recent pollution reports.
"""

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import DBSCAN

from app.utils.constants import HOTSPOT_DBSCAN_EPS_KM, HOTSPOT_DBSCAN_MIN_SAMPLES, SeverityLevel
from app.utils.helpers import cluster_centroid, haversine_distance_km
from app.utils.logger import logger

_SEVERITY_WEIGHT = {
    SeverityLevel.LOW: 0.3,
    SeverityLevel.MEDIUM: 0.6,
    SeverityLevel.HIGH: 1.0,
}


@dataclass
class ReportPoint:            #view
    
    report_id: int
    latitude: float
    longitude: float
    severity: SeverityLevel
    confidence: float


@dataclass
class HotspotCluster:
    latitude: float
    longitude: float
    cluster_size: int
    risk_score: float
    member_report_ids: list[int]


def _haversine_distance_matrix(points: list[ReportPoint]) -> np.ndarray:
  
    """Build an NxN haversine distance matrix (in km) for DBSCAN's precomputed metric."""
    
    n = len(points)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = haversine_distance_km(
                points[i].latitude, points[i].longitude, points[j].latitude, points[j].longitude
            )
            matrix[i, j] = dist
            matrix[j, i] = dist
    return matrix


def detect_hotspots(
    points: list[ReportPoint],
    eps_km: float = HOTSPOT_DBSCAN_EPS_KM,
    min_samples: int = HOTSPOT_DBSCAN_MIN_SAMPLES,
) -> list[HotspotCluster]:
   
    """
    Run DBSCAN over report locations and return one HotspotCluster per
    non-noise cluster found.

    Args:
        points: candidate report points (e.g. last 7/30 days of reports).
        eps_km: neighborhood radius in kilometers.
        min_samples: minimum points required to form a dense cluster.
    """
    
    if len(points) < min_samples:
        logger.info(f"Not enough reports ({len(points)}) to form a hotspot (need >= {min_samples}).")
        return []

    distance_matrix = _haversine_distance_matrix(points)
    db = DBSCAN(eps=eps_km, min_samples=min_samples, metric="precomputed")
    labels = db.fit_predict(distance_matrix)

    clusters: dict[int, list[ReportPoint]] = {}
    for label, point in zip(labels, points):
        if label == -1:
            continue                          # noise point, not part of any cluster
        clusters.setdefault(label, []).append(point)

    hotspots: list[HotspotCluster] = []
    for member_points in clusters.values():
        centroid_lat, centroid_lon = cluster_centroid(
            [(p.latitude, p.longitude) for p in member_points]
        )
        risk_score = _compute_risk_score(member_points)
        hotspots.append(
            HotspotCluster(
                latitude=centroid_lat,
                longitude=centroid_lon,
                cluster_size=len(member_points),
                risk_score=risk_score,
                member_report_ids=[p.report_id for p in member_points],
            )
        )

    logger.info(f"DBSCAN found {len(hotspots)} hotspot(s) from {len(points)} reports.")
    return sorted(hotspots, key=lambda h: h.risk_score, reverse=True)


def _compute_risk_score(points: list[ReportPoint]) -> float:
    """
    Risk score (0-100) blends:
    - cluster size (more reports -> higher risk, saturating contribution)
    - average severity weight of member reports
    - average detection confidence
    """
    size_score = min(len(points) / 10, 1.0)                 # saturates at 10+ reports
    severity_score = sum(_SEVERITY_WEIGHT[p.severity] for p in points) / len(points)
    confidence_score = sum(p.confidence for p in points) / len(points)

    blended = (0.4 * size_score) + (0.4 * severity_score) + (0.2 * confidence_score)
    return round(blended * 100, 2)


if __name__ == "__main__":
    
    # 1. Create some dummy pollution reports (close to each other)
    test_points = [
        ReportPoint(report_id=1, latitude=28.7041, longitude=77.1025, severity=SeverityLevel.HIGH, confidence=0.9),
        ReportPoint(report_id=2, latitude=28.7045, longitude=77.1029, severity=SeverityLevel.MEDIUM, confidence=0.8),
        ReportPoint(report_id=3, latitude=28.7040, longitude=77.1020, severity=SeverityLevel.HIGH, confidence=0.95),
        # And one outlier far away (noise point)
        ReportPoint(report_id=4, latitude=18.9220, longitude=72.8347, severity=SeverityLevel.LOW, confidence=0.5),
    ]

    
    # 2. Run the detector
    print("Running hotspot detection...")
    detected_hotspots = detect_hotspots(test_points, eps_km=5.0, min_samples=2)

    
    # 3. Print the results
    print(f"\nFound {len(detected_hotspots)} hotspot(s):")
    for hotspot in detected_hotspots:
        print(f" - Center: ({hotspot.latitude:.4f}, {hotspot.longitude:.4f})")
        print(f" - Size: {hotspot.cluster_size} reports")
        print(f" - Risk Score: {hotspot.risk_score}/100")
        print(f" - Report IDs: {hotspot.member_report_ids}\n")
