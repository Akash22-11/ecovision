"""Tests for the 24h AQI prediction endpoint and history."""


def test_predict_tomorrow_returns_forecast(client, auth_headers):
    response = client.post(
        "/api/v1/prediction/tomorrow",
        headers=auth_headers,
        json={"latitude": 22.5726, "longitude": 88.3639, "location_name": "Kolkata Central"},
    )
    assert response.status_code == 200
    body = response.json()

    assert body["location"] == "Kolkata Central"
    assert body["predicted_aqi"] >= 0
    assert body["risk_level"] in {"low", "moderate", "high", "severe"}
    assert 0 <= body["confidence_score"] <= 1


def test_predict_tomorrow_requires_authentication(client):
    response = client.post(
        "/api/v1/prediction/tomorrow", json={"latitude": 22.5726, "longitude": 88.3639}
    )
    assert response.status_code == 401


def test_predict_tomorrow_rejects_invalid_latitude(client, auth_headers):
    response = client.post(
        "/api/v1/prediction/tomorrow",
        headers=auth_headers,
        json={"latitude": 999, "longitude": 88.3639},
    )
    assert response.status_code == 422


def test_prediction_history_reflects_past_predictions(client, auth_headers):
    client.post(
        "/api/v1/prediction/tomorrow",
        headers=auth_headers,
        json={"latitude": 22.5726, "longitude": 88.3639},
    )
    response = client.get("/api/v1/prediction/history", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["predictions"]) == 1
