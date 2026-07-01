" AQI predictor: "

import pickle
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import settings
from app.utils.helpers import risk_level_from_aqi
from app.utils.logger import logger

_model_cache: dict[str, Any] = {}

FEATURE_ORDER = ["aqi", "pm25", "pm10", "temperature", "humidity", "wind_speed"]


def _load_model():
    """Lazily load and cache the trained Random Forest model. Returns None if missing."""
    if "model" in _model_cache:
        return _model_cache["model"]

    model_path = Path(settings.AQI_MODEL_PATH)
    if not model_path.exists():
        logger.warning(
            f"AQI model not found at '{model_path}'. Run `python ml/train.py` to train one. "
            "Falling back to heuristic mock prediction."
        )
        _model_cache["model"] = None
        return None

    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        _model_cache["model"] = model
        logger.info(f"Loaded AQI prediction model from {model_path}")
        return model
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Failed to load AQI model ({exc}). Falling back to mock prediction.")
        _model_cache["model"] = None
        return None


def predict_next_24h_aqi(
    aqi: float, pm25: float, pm10: float, temperature: float, humidity: float, wind_speed: float
) -> dict[str, Any]:
    """
    Predict AQI 24 hours ahead from current sensor readings.

    Returns:
        {"predicted_aqi": float, "risk_level": RiskLevel, "confidence_score": float}
    """
    model = _load_model()
    features = pd.DataFrame(
        [[aqi, pm25, pm10, temperature, humidity, wind_speed]], columns=FEATURE_ORDER
    )

    if model is None:
        predicted_aqi = _heuristic_prediction(aqi, pm25, pm10, wind_speed)
        confidence_score = 0.55  # lower confidence to signal this is a non-ML fallback
    else:
        predicted_aqi = float(model.predict(features)[0])
        confidence_score = _estimate_confidence(model, features)

    predicted_aqi = max(0.0, round(predicted_aqi, 1))

    return {
        "predicted_aqi": predicted_aqi,
        "risk_level": risk_level_from_aqi(predicted_aqi),
        "confidence_score": round(confidence_score, 2),
    }


def _heuristic_prediction(aqi: float, pm25: float, pm10: float, wind_speed: float) -> float:
    """
    Simple physically-motivated fallback used only when no trained model exists:
    particulate load pushes AQI up, wind disperses it down.
    """
    particulate_pressure = (pm25 * 1.2 + pm10 * 0.8) / 2
    dispersion_relief = wind_speed * 3.5
    return aqi * 0.6 + particulate_pressure * 0.4 - dispersion_relief * 0.1


def _estimate_confidence(model, features: pd.DataFrame) -> float:
    """
    For a RandomForestRegressor, use agreement across individual trees as a
    proxy for prediction confidence: lower variance among trees -> higher confidence.
    """
    try:
        feature_values = features.values
        tree_predictions = [tree.predict(feature_values)[0] for tree in model.estimators_]
        spread = max(tree_predictions) - min(tree_predictions)
        # Normalize: a 0 spread -> confidence 0.99; a >=100 AQI-point spread -> confidence 0.5
        confidence = 0.99 - min(spread / 100, 0.49)
        return confidence
    except Exception:  # noqa: BLE001 - non-RandomForest models won't have .estimators_
        return 0.75
