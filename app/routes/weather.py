from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.weather import CurrentAirQualityResponse
from app.services.weather_service import fetch_current_air_quality

router = APIRouter(prefix="/weather", tags=["Air Quality"])


@router.get(
    "/current",
    response_model=CurrentAirQualityResponse,
    summary="Get current AQI and weather for a location",
    description=(
        "Fetches AQI, PM2.5, PM10, CO, NO2, temperature, humidity and wind speed "
        "from OpenWeather for the given coordinates, and stores the reading for "
        "historical trend/prediction use."
    ),
)

def get_current_air_quality(
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> CurrentAirQualityResponse:
    data = fetch_current_air_quality(db, latitude, longitude)
    return CurrentAirQualityResponse(**data)
