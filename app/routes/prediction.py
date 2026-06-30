"""AQI Prediction routes: forecast next-24h AQI and view prediction history."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.prediction import PredictionHistoryResponse, PredictionRequest, PredictionResponse
from app.services.prediction_service import get_prediction_history, predict_for_location

router = APIRouter(prefix="/prediction", tags=["AQI Prediction"])


@router.post(
    "/tomorrow",
    response_model=PredictionResponse,
    summary="Predict AQI for the next 24 hours at a location",
    description=(
        "Fetches current conditions for the given coordinates and runs the trained "
        "Random Forest model to forecast AQI 24 hours ahead, with a risk level and "
        "confidence score."
    ),
)
def predict_tomorrow(
    payload: PredictionRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> PredictionResponse:
    prediction = predict_for_location(db, payload.latitude, payload.longitude, payload.location_name)
    return PredictionResponse.model_validate(prediction)


@router.get(
    "/history",
    response_model=PredictionHistoryResponse,
    summary="Get historical AQI predictions",
    description="Backs the historical prediction graph on the dashboard.",
)
def prediction_history(
    limit: int = 30, db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)
) -> PredictionHistoryResponse:
    predictions = get_prediction_history(db, limit=limit)
    return PredictionHistoryResponse(predictions=[PredictionResponse.model_validate(p) for p in predictions])
