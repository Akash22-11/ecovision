"""Tests for DBSCAN-based hotspot generation and ranking."""

from pathlib import Path

SAMPLE_IMAGE = Path(__file__).parent / "sample_image.jpg"

# A tight cluster of nearby coordinates (within ~100m of each other) in Kolkata,
# well within HOTSPOT_DBSCAN_EPS_KM, so DBSCAN should group them into one hotspot.
CLUSTER_COORDS = [
    (22.5726, 88.3639),
    (22.5728, 88.3641),
    (22.5724, 88.3637),
    (22.5727, 88.3640),
]


def _upload_at(client, headers, lat, lon):
    with open(SAMPLE_IMAGE, "rb") as f:
        return client.post(
            "/api/v1/reports/upload",
            headers=headers,
            files={"image": ("sample.jpg", f, "image/jpeg")},
            data={"latitude": lat, "longitude": lon},
        )


def test_generate_hotspots_requires_admin(client, auth_headers):
    response = client.post("/api/v1/hotspots/generate", headers=auth_headers)
    assert response.status_code == 403


def test_generate_hotspots_creates_cluster_from_nearby_reports(client, auth_headers, admin_headers):
    for lat, lon in CLUSTER_COORDS:
        upload = _upload_at(client, auth_headers, lat, lon)
        assert upload.status_code == 201

    response = client.post("/api/v1/hotspots/generate", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()

    assert body["hotspots_created"] >= 1
    hotspot = body["hotspots"][0]
    assert hotspot["cluster_size"] >= 3
    assert 0 <= hotspot["risk_score"] <= 100
    assert hotspot["status"] == "active"


def test_generate_hotspots_with_too_few_reports_creates_none(client, auth_headers, admin_headers):
    _upload_at(client, auth_headers, 22.5726, 88.3639)

    response = client.post("/api/v1/hotspots/generate", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["hotspots_created"] == 0


def test_list_hotspots_ranked_by_risk_score(client, auth_headers, admin_headers):
    for lat, lon in CLUSTER_COORDS:
        _upload_at(client, auth_headers, lat, lon)
    client.post("/api/v1/hotspots/generate", headers=admin_headers)

    response = client.get("/api/v1/hotspots", headers=auth_headers)
    assert response.status_code == 200
    hotspots = response.json()
    risk_scores = [h["risk_score"] for h in hotspots]
    assert risk_scores == sorted(risk_scores, reverse=True)
