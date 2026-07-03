"""Tests for the pollution report upload pipeline (runs YOLO detector in mock mode)."""

from pathlib import Path

SAMPLE_IMAGE = Path(__file__).parent / "sample_image.jpg"


def _upload_sample_report(client, headers, latitude=22.5726, longitude=88.3639):
    with open(SAMPLE_IMAGE, "rb") as f:
        return client.post(
            "/api/v1/reports/upload",
            headers=headers,
            files={"image": ("sample.jpg", f, "image/jpeg")},
            data={"latitude": latitude, "longitude": longitude, "description": "Test report"},
        )


def test_upload_report_runs_detection_and_persists(client, auth_headers):
    response = _upload_sample_report(client, auth_headers)
    assert response.status_code == 201
    body = response.json()

    assert body["report"]["latitude"] == 22.5726
    assert body["report"]["status"] == "pending"
    assert 0 <= body["detection"]["confidence"] <= 100
    assert body["detection"]["severity"] in {"low", "medium", "high"}
    # No trained YOLOv8 weights are bundled with this repo, so mock mode is expected.
    assert body["detection"]["mock"] is True


def test_upload_report_rejects_unsupported_file_type(client, auth_headers):
    response = client.post(
        "/api/v1/reports/upload",
        headers=auth_headers,
        files={"image": ("notes.txt", b"not an image", "text/plain")},
        data={"latitude": 22.5726, "longitude": 88.3639},
    )
    assert response.status_code == 400


def test_upload_report_requires_authentication(client):
    with open(SAMPLE_IMAGE, "rb") as f:
        response = client.post(
            "/api/v1/reports/upload",
            files={"image": ("sample.jpg", f, "image/jpeg")},
            data={"latitude": 22.5726, "longitude": 88.3639},
        )
    assert response.status_code == 401


def test_list_reports_returns_uploaded_report(client, auth_headers):
    _upload_sample_report(client, auth_headers)
    response = client.get("/api/v1/reports", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_single_report(client, auth_headers):
    upload = _upload_sample_report(client, auth_headers)
    report_id = upload.json()["report"]["id"]

    response = client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == report_id


def test_get_missing_report_returns_404(client, auth_headers):
    response = client.get("/api/v1/reports/99999", headers=auth_headers)
    assert response.status_code == 404


def test_owner_can_delete_own_report(client, auth_headers):
    upload = _upload_sample_report(client, auth_headers)
    report_id = upload.json()["report"]["id"]

    response = client.delete(f"/api/v1/reports/{report_id}", headers=auth_headers)
    assert response.status_code == 204

    follow_up = client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)
    assert follow_up.status_code == 404


def test_admin_can_update_report_status(client, auth_headers, admin_headers):
    upload = _upload_sample_report(client, auth_headers)
    report_id = upload.json()["report"]["id"]

    response = client.patch(
        f"/api/v1/reports/{report_id}/status", headers=admin_headers, json={"status": "verified"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "verified"


def test_citizen_cannot_update_report_status(client, auth_headers):
    upload = _upload_sample_report(client, auth_headers)
    report_id = upload.json()["report"]["id"]

    response = client.patch(
        f"/api/v1/reports/{report_id}/status", headers=auth_headers, json={"status": "verified"}
    )
    assert response.status_code == 403
