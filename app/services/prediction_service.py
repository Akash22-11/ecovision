"""Prediction service: orchestrates 24h AQI forecasting, persistence, and history retrieval."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.ai.aqi_predictor import predict_next_24h_aqi
from app.models.prediction import Prediction
from app.models.sensor_data import SensorData
from app.services.weather_service import fetch_current_air_quality
from app.utils.logger import logger
from app.utils.validators import ValidationError


def predict_for_location(
    db: Session, latitude: float, longitude: float, location_name: str | None = None
) -> Prediction:
    
    """
    Fetch current conditions for a location, run the Random Forest model
    to predict AQI 24h ahead, and persist the result.
    """
    current = fetch_current_air_quality(db, latitude, longitude)

    result = predict_next_24h_aqi(
        aqi=current["aqi"],
        pm25=current["pm25"],
        pm10=current["pm10"],
        temperature=current["temperature"],
        humidity=current["humidity"],
        wind_speed=current["wind_speed"],
    )

    prediction = Prediction(
        location=location_name or f"{latitude:.4f},{longitude:.4f}",
        latitude=latitude,
        longitude=longitude,
        predicted_aqi=result["predicted_aqi"],
        confidence_score=result["confidence_score"],
        risk_level=result["risk_level"],
        prediction_time=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=24),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    logger.info(
        f"Predicted AQI={result['predicted_aqi']} (risk={result['risk_level'].value}) "
        f"for ({latitude}, {longitude})"
    )
    return prediction


def get_prediction_history(db: Session, limit: int = 30) -> list[Prediction]:
    return db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
