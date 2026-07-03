# EcoVision - Backend

> **EcoVision** is an AI-powered pollution monitoring and prediction platform. 

This backend service processes citizen-reported pollution incidents via geotagged photos. It utilizes a YOLOv8 detector to classify pollution types, DBSCAN to cluster reports into actionable geographic hotspots, and a Random Forest model to forecast the Air Quality Index (AQI) 24 hours ahead. Municipality administrators are empowered with a comprehensive dashboard, an interactive map, and auto-generated, recommendation-backed alerts to drive civic action.

---

## 🚀 Key Features

*   **User Management:** Registration and login for citizens and municipality admins, featuring JWT authentication and role-based access control.
*   **Pollution Reporting:** Upload photos with GPS coordinates and timestamps. Includes category assignment, optional descriptions, and a status lifecycle (Pending → Verified → Resolved).
*   **AI Image Analysis:** YOLOv8 detection of smoke, dust, garbage burning, construction dust, and industrial smoke, complete with confidence scores and severity levels.
*   **Interactive Pollution Map:** Filterable marker data (by type, severity, and date) ready for front-end map UI integration.
*   **Air Quality Integration:** Live fetching of AQI, PM2.5, PM10, CO, NO₂, temperature, humidity, and wind speed via OpenWeather.
*   **Hotspot Detection:** DBSCAN clustering to identify high-risk pollution zones, complete with risk scoring, ranking, and historical tracking.
*   **Predictive Analytics:** 24-hour ahead AQI forecasting utilizing a Random Forest model, providing risk levels, confidence scores, and historical trend data.
*   **Admin Dashboard:** Aggregated totals, daily report tracking, active hotspot monitoring, current AQI, trend charts, and category/severity breakdowns.
*   **Automated Alerts:** Rule-based recommended actions generated automatically from high-risk hotspots, complete with resolution tracking for municipal authorities.

---

## 🛠️ Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Core Framework** | Python 3.12, FastAPI, Pydantic v2 |
| **Database & ORM** | PostgreSQL, SQLAlchemy 2.0, Alembic |
| **AI & Machine Learning** | OpenCV, Ultralytics YOLOv8, scikit-learn (Random Forest, DBSCAN), pandas, NumPy |
| **Security & Utilities** | JWT, Loguru, Pytest |
| **DevOps** | Docker, Docker Compose |

---


---
## Contributing to EcoVision 🌍

Thank you for your interest in contributing to EcoVision! We are building a platform to empower citizens and municipalities to monitor and predict pollution. This guide outlines our development workflow.


## 🛠️ Development Workflow

1. **Branching Strategy:**
   Always create a new branch for your work. Do not commit directly to `main`.
   * Feature: `feature/short-description` (e.g., `feature/map-clustering`)
   * Bug Fix: `bugfix/issue-description` (e.g., `bugfix/jwt-expiry-fix`)
   * ML/Data: `model/yolo-retrain`

2. **Local Setup:**
   Please refer to the `README.md` for instructions on setting up the project locally via Docker or a virtual environment.

3. **Code Style & Formatting:**
   We enforce clean, readable Python code.
   * Format your code using **Black**: `black app/ ml/ tests/`
   * Lint your code using **Flake8** or **Ruff**.
   * Use type hints for all FastAPI endpoints and service functions (Pydantic models will handle the heavy lifting).

4. **Testing:**
   Before opening a Pull Request, ensure all tests pass.
   ```bash
   pytest -q
---

# EcoVision System Architecture 🏗️

EcoVision is designed as a modular, asynchronous backend capable of handling geospatial data, image processing, and machine learning inference.


## 🔄 System Flow

1. **Data Ingestion (Citizen App):** 
   A user uploads an image and GPS coordinates to `/reports/upload`.
2. **AI Inference Pipeline:** 
   * The image is saved to `app/uploads/original/`.
   * The path is passed to the YOLOv8 service.
   * YOLOv8 identifies pollution classes (e.g., *garbage burning*), assigns a confidence score, and determines severity.
   * The processed image with bounding boxes is saved to `app/uploads/processed/`.
3. **Storage:** 
   The report metadata, GPS coordinates, and image paths are persisted to PostgreSQL via SQLAlchemy.
4. **Hotspot Generation (Cron/Admin Trigger):** 
   * The `/hotspots/generate` endpoint pulls recent reports.
   * The **DBSCAN** algorithm clusters reports based on geospatial proximity (Haversine distance).
   * Clusters are assigned a Risk Score based on the density and severity of the reports.
5. **Prediction Pipeline:** 
   * OpenWeather API fetches current meteorological data.
   * The **Random Forest** model processes current AQI, weather, and historical trends to output a 24-hour AQI prediction.
6. **Municipality Dashboard:** 
   * The admin frontend fetches aggregated data via the `/dashboard/*` and `/municipality/alerts` endpoints.

## 🗄️ Database Schema Overview

* **Users:** Citizens and Admins (differentiated by role).
* **PollutionReports:** Geolocation (lat/lon), image paths, AI-detected category, severity, status (Pending/Verified/Resolved).
* **Hotspots:** Centroid lat/lon, calculated radius, risk score, list of associated report IDs.
* **Alerts:** Auto-generated action items tied to high-risk hotspots.
* **Predictions:** Historical log of predicted AQI vs. actual AQI.
## 📂 Project Structure

```text
backend/
├── app/
│   ├── main.py                # FastAPI app, routers, CORS, exception handlers
│   ├── config.py              # Pydantic Settings (env-driven config)
│   ├── database.py            # SQLAlchemy engine/session/Base
│   ├── dependencies.py        # Auth + role-based access dependencies
│   ├── routes/                # API route definitions
│   ├── models/                # Database models
│   ├── schemas/               # Pydantic request/response validation models
│   ├── services/              # Core business logic
│   ├── ai/                    # YOLO detector, DBSCAN clustering, RF predictor
│   ├── utils/                 # Logger, constants, helpers, security
│   └── uploads/               # Original and processed (annotated) images
├── ml/
│   ├── train.py               # Trains the RF AQI model (generates synthetic dataset if missing)
│   ├── dataset.csv            # Training data
│   └── model.pkl              # Trained model, loaded at runtime
├── alembic/                   # Database migrations
├── tests/                     # Pytest suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt


