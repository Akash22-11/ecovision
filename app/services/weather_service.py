"""
Weather service: fetches current AQI + weather from OpenWeather, persists
a SensorData row for historical trend/prediction use, and falls back to a
deterministic mock reading when no API key is configured.
"""

import random

import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.models.sensor_data import SensorData
from app.utils.logger import logger

REQUEST_TIMEOUT_SECONDS = 8


def fetch_current_air_quality(db: Session, latitude: float, longitude: float) -> dict:
    """
    Fetch current AQI + weather for a location, persist it as SensorData,
    and return a flat dict matching CurrentAirQualityResponse.
    """
    if not settings.OPENWEATHER_API_KEY:
        logger.warning("OPENWEATHER_API_KEY not set - returning mock air quality data.")
        data = _mock_reading(latitude, longitude)
    else:
        try:
            data = _fetch_from_openweather(latitude, longitude)
        except requests.RequestException as exc:
            logger.error(f"OpenWeather request failed ({exc}); falling back to mock data.")
            data = _mock_reading(latitude, longitude)

    _persist_sensor_reading(db, data)
    return data


def _fetch_from_openweather(latitude: float, longitude: float) -> dict:
    """Call OpenWeather's Air Pollution + current weather endpoints and merge results."""
    base = settings.OPENWEATHER_BASE_URL
    key = settings.OPENWEATHER_API_KEY

    air_resp = requests.get(
        f"{base}/air_pollution",
        params={"lat": latitude, "lon": longitude, "appid": key},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    air_resp.raise_for_status()
    air = air_resp.json()["list"][0]

    weather_resp = requests.get(
        f"{base}/weather",
        params={"lat": latitude, "lon": longitude, "appid": key, "units": "metric"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    weather_resp.raise_for_status()
    weather = weather_resp.json()

    components = air["components"]
    return {
        "latitude": latitude,
        "longitude": longitude,
        "aqi": _owm_aqi_to_scale(air["main"]["aqi"]),
        "pm25": components.get("pm2_5", 0.0),
        "pm10": components.get("pm10", 0.0),
        "co": components.get("co", 0.0),
        "no2": components.get("no2", 0.0),
        "temperature": weather["main"]["temp"],
        "humidity": weather["main"]["humidity"],
        "wind_speed": weather["wind"]["speed"],
        "source": "openweather",
    }


def _owm_aqi_to_scale(owm_index: int) -> float:
    """
    OpenWeather's AQI index is a 1-5 scale; convert to an approximate
    0-500 scale (CPCB/US-AQI style) for consistency with risk_level_from_aqi().
    """
    mapping = {1: 40, 2: 90, 3: 150, 4: 230, 5: 350}
    return float(mapping.get(owm_index, 100))


def _mock_reading(latitude: float, longitude: float) -> dict:
    """Deterministic-ish mock reading for local development without an API key."""
    return {
        "latitude": latitude,
        "longitude": longitude,
        "aqi": round(random.uniform(60, 220), 1),
        "pm25": round(random.uniform(15, 120), 1),
        "pm10": round(random.uniform(25, 180), 1),
        "co": round(random.uniform(0.2, 2.5), 2),
        "no2": round(random.uniform(5, 60), 1),
        "temperature": round(random.uniform(18, 38), 1),
        "humidity": round(random.uniform(30, 85), 1),
        "wind_speed": round(random.uniform(0.5, 6.0), 1),
        "source": "mock",
    }


def _persist_sensor_reading(db: Session, data: dict) -> SensorData:
    reading = SensorData(
        latitude=data["latitude"],
        longitude=data["longitude"],
        aqi=data["aqi"],
        pm25=data["pm25"],
        pm10=data["pm10"],
        co=data["co"],
        no2=data["no2"],
        temperature=data["temperature"],
        humidity=data["humidity"],
        wind_speed=data["wind_speed"],
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


def latest_known_aqi(db: Session) -> float | None:
    """Most recent AQI reading across all locations - used by the dashboard."""
    latest = db.query(SensorData).order_by(SensorData.timestamp.desc()).first()
    return latest.aqi if latest else None
