from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "EcoVision AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security / JWT ---
    SECRET_KEY: str  # required — from .env locally, Render env var in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # --- Database ---
    DATABASE_URL: str  # required — from .env locally, Render env var in production

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # --- File uploads ---
    UPLOAD_ORIGINAL_DIR: str = "app/uploads/original"
    UPLOAD_PROCESSED_DIR: str = "app/uploads/processed"

    # --- YOLO ---
    YOLO_MODEL_PATH: str = "ml/pollution_yolov8.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.35

    # --- AQI ---
    AQI_MODEL_PATH: str = "ml/model.pkl"

    # --- Weather API ---
    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
