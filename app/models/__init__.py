"""
Import all models here so that `Base.metadata` is fully populated for
Alembic autogenerate and for `Base.metadata.create_all()` in tests/dev.
"""

from app.models.alert import Alert
from app.models.hotspot import Hotspot
from app.models.pollution_report import PollutionReport
from app.models.prediction import Prediction
from app.models.sensor_data import SensorData
from app.models.user import User

__all__ = ["User", "PollutionReport", "SensorData", "Hotspot", "Prediction", "Alert"]
