"""
Rule-based recommendation engine.

Maps a hotspot's dominant pollution type (and AQI context) to a
recommended municipal action and a human-readable alert message.
Deliberately simple/rule-based per spec - no ML involved here.
"""

from dataclasses import dataclass

from app.utils.constants import AQI_PUBLIC_HEALTH_WARNING_THRESHOLD, PollutionType

_ACTION_BY_TYPE: dict[PollutionType, str] = {
    PollutionType.SMOKE: "Deploy Fire Brigade",
    PollutionType.DUST: "Deploy Water Mist Cannon",
    PollutionType.GARBAGE_BURNING: "Dispatch Cleanup Team",
    PollutionType.CONSTRUCTION_DUST: "Deploy Water Mist Cannon + Site Inspection",
    PollutionType.INDUSTRIAL_SMOKE: "Dispatch Inspection Team",
    PollutionType.OTHER: "Dispatch Inspection Team",
}


@dataclass
class Recommendation:
    recommended_action: str
    message: str


def recommend_action(
    dominant_pollution_type: PollutionType,
    risk_score: float,
    cluster_size: int,
    current_aqi: float | None = None,
) -> Recommendation:
   
    """
    Build a recommended action + alert message for a hotspot.

    Args:
        dominant_pollution_type: most frequent pollution_type among the
            hotspot's member reports.
        risk_score: hotspot risk score (0-100) from app/ai/hotspot_detector.py.
        cluster_size: number of reports composing the hotspot.
        current_aqi: latest known AQI near the hotspot, if available.
    """
    action = _ACTION_BY_TYPE.get(dominant_pollution_type, "Dispatch Inspection Team")

    message = (
        f"High-risk {dominant_pollution_type.value.replace('_', ' ')} hotspot detected "
        f"({cluster_size} reports, risk score {risk_score:.0f}/100). "
        f"Recommended action: {action}."
    )

    if current_aqi is not None and current_aqi > AQI_PUBLIC_HEALTH_WARNING_THRESHOLD:
        message += f" AQI is {current_aqi:.0f} - issue a Public Health Warning for this area."

    return Recommendation(recommended_action=action, message=message)


# --- TEST BLOCK ---
if __name__ == "__main__":
    
    # Test Case 1: Critical Garbage Burning with high AQI
    rec1 = recommend_action(
        dominant_pollution_type=PollutionType.GARBAGE_BURNING,
        risk_score=85.5,
        cluster_size=12,
        current_aqi=350.0  # Assuming threshold is lower than this
    )
    print("--- Test Case 1 ---")
    print(f"Action:  {rec1.recommended_action}")
    print(f"Message: {rec1.message}\n")

    # Test Case 2: Low-risk Construction Dust, no AQI data
    rec2 = recommend_action(
        dominant_pollution_type=PollutionType.CONSTRUCTION_DUST,
        risk_score=25.0,
        cluster_size=3,
        current_aqi=None
    )
    print("--- Test Case 2 ---")
    print(f"Action:  {rec2.recommended_action}")
    print(f"Message: {rec2.message}\n")
