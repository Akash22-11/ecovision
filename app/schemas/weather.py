from pydantic import BaseModel, Field


class CurrentAirQualityResponse(BaseModel):
    latitude: float
    longitude: float
    aqi: float = Field(..., description="Composite Air Quality Index")
    pm25: float
    pm10: float
    co: float
    no2: float
    temperature: float = Field(..., description="Degrees Celsius")
    humidity: float = Field(..., description="Percent")
    wind_speed: float = Field(..., description="Meters per second")
    source: str = Field(default="openweather", description="Data source, or 'mock' if no API key configured.")
