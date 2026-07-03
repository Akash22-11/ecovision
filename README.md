# EcoVision AI - Backend

An AI-powered pollution monitoring and prediction backend built with FastAPI. Citizens
report pollution incidents with geotagged photos; a YOLOv8 detector classifies the
pollution type, DBSCAN clusters reports into hotspots, and a Random Forest model
forecasts AQI 24 hours ahead. Municipality admins get a dashboard, an interactive map,
and auto-generated, recommendation-backed alerts.

## Features

- **User Management** - citizen/municipality-admin registration & login, JWT auth, role-based access control
- **Pollution Reporting** - photo upload with GPS + timestamp, category, optional description, status lifecycle (Pending → Verified → Resolved)
- **AI Image Analysis** - YOLOv8 detection of smoke, dust, garbage burning, construction dust, and industrial smoke, with confidence score and severity level
- **Interactive Pollution Map** - filterable (type / severity / date) marker data for a map UI
- **Air Quality Integration** - current AQI, PM2.5, PM10, CO, NO₂, temperature, humidity, wind speed (OpenWeather)
- **Hotspot Detection** - DBSCAN clustering, risk scoring, ranking, history
- **Dashboard** - totals, today's reports, active hotspots, current AQI, trend chart, breakdowns by category/severity
- **AQI Prediction** - 24h-ahead forecast with risk level, confidence score, and historical graph data
- **Municipality Alerts** - auto-generated from high-risk hotspots, with rule-based recommended actions and resolution tracking

## Tech Stack

Python 3.12 · FastAPI · SQLAlchemy 2.0 · Alembic · PostgreSQL · JWT · Pydantic v2 ·
OpenCV · Ultralytics YOLOv8 · scikit-learn (Random Forest, DBSCAN) · pandas/NumPy ·
Loguru · Docker · pytest

## Project Structure

```
backend/
├── app/
│   ├── main.py                 FastAPI app, routers, CORS, exception handlers
│   ├── config.py                Pydantic Settings (env-driven config)
│   ├── database.py              SQLAlchemy engine/session/Base
│   ├── dependencies.py          Auth + role-based access dependencies
│   ├── routes/                  auth, reports, weather, hotspots, prediction, dashboard, municipality
│   ├── models/                  user, pollution_report, sensor_data, hotspot, prediction, alert
│   ├── schemas/                 Pydantic request/response models
│   ├── services/                business logic (auth, upload, report, weather, hotspot, prediction, alert, dashboard, map)
│   ├── ai/                      yolo_detector, hotspot_detector (DBSCAN), aqi_predictor (Random Forest), recommendation_engine
│   ├── utils/                   logger, constants, helpers, validators, security
│   └── uploads/                 original/ and processed/ (annotated) images
├── ml/
│   ├── train.py                 Trains the Random Forest AQI model (generates a synthetic dataset if none exists)
│   ├── dataset.csv              Training data
│   └── model.pkl                Trained model, loaded at runtime
├── alembic/                     DB migrations
├── tests/                       pytest suite (auth, reports, hotspots, prediction)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Installation (local, without Docker)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then edit DATABASE_URL, SECRET_KEY, OPENWEATHER_API_KEY, etc.

# Provision a local PostgreSQL database matching your .env, then:
alembic upgrade head

# Train the AQI prediction model (bootstraps a synthetic dataset on first run):
python ml/train.py

uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs` (Swagger) or `http://localhost:8000/redoc`.

## Docker Setup

```bash
cp .env.example .env   # edit as needed; defaults work out of the box for local dev
docker compose up --build
```

This starts a PostgreSQL container and the backend, runs `alembic upgrade head`
automatically on boot, and exposes the API on `http://localhost:8000`.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | `development` / `production` / `testing` | `development` |
| `SECRET_KEY` | JWT signing secret - **change in production** | dev placeholder |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `1440` |
| `DATABASE_URL` | SQLAlchemy connection string | local Postgres |
| `CORS_ORIGINS` | Comma-separated allowed origins, or `*` | `*` |
| `YOLO_MODEL_PATH` | Path to a YOLOv8 model fine-tuned on pollution classes | `ml/pollution_yolov8.pt` |
| `YOLO_CONFIDENCE_THRESHOLD` | Minimum detection confidence (0-1) | `0.35` |
| `AQI_MODEL_PATH` | Path to the trained Random Forest model | `ml/model.pkl` |
| `OPENWEATHER_API_KEY` | OpenWeather API key | empty (mock mode) |

### A note on AI "mock mode"

- **YOLOv8**: stock COCO weights don't contain pollution classes. Until you supply a
  model fine-tuned on a pollution dataset at `YOLO_MODEL_PATH`, `/reports/upload`
  returns a clearly-flagged (`"mock": true`) plausible detection so the rest of the
  pipeline (severity, storage, hotspots, alerts) is fully exercisable end-to-end.
- **AQI prediction**: until `python ml/train.py` has been run, `/prediction/tomorrow`
  falls back to a simple particulate/wind heuristic with a deliberately lower
  confidence score, rather than failing the request.
- **Weather**: without `OPENWEATHER_API_KEY`, `/weather/current` returns deterministic
  mock readings instead of failing.

## API Documentation

All endpoints are under the `/api/v1` prefix and documented interactively at `/docs`.

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register a citizen or municipality admin | - |
| POST | `/auth/login` | Log in, returns JWT | - |
| GET | `/auth/profile` | Current user's profile | Any |
| POST | `/reports/upload` | Upload a report photo; runs YOLOv8 automatically | Any |
| GET | `/reports` | List reports (filter by type/severity/status/date) | Any |
| GET | `/reports/{id}` | Get a single report | Any |
| PATCH | `/reports/{id}/status` | Update report status | Admin |
| DELETE | `/reports/{id}` | Delete a report (owner or admin) | Any |
| GET | `/weather/current` | Current AQI + weather for a location | Any |
| POST | `/hotspots/generate` | Run DBSCAN clustering over recent reports | Admin |
| GET | `/hotspots` | List hotspots, ranked by risk score | Any |
| POST | `/prediction/tomorrow` | Predict AQI 24h ahead for a location | Any |
| GET | `/prediction/history` | Historical predictions | Any |
| GET | `/dashboard/stats` | Top-line dashboard stats | Any |
| GET | `/dashboard/charts` | Category/severity breakdowns + trend | Any |
| GET | `/dashboard/map` | Filterable map marker data | Any |
| GET | `/municipality/alerts` | List alerts (auto-generates from high-risk hotspots) | Admin |
| POST | `/municipality/resolve` | Mark an alert resolved | Admin |

## Testing

```bash
pytest -q
```

The suite covers authentication & RBAC, the report upload/detection pipeline,
DBSCAN hotspot clustering, and AQI prediction - 25 tests, run against an isolated
in-memory SQLite database per test (no external services required; YOLOv8 runs in
mock mode automatically since no trained weights are bundled in this repo).

## Deployment Guide

1. Provision a managed PostgreSQL instance and a host/VM (or container platform)
   for the backend.
2. Set production environment variables (especially `SECRET_KEY`, `DATABASE_URL`,
   `OPENWEATHER_API_KEY`, and `CORS_ORIGINS`) via your platform's secrets manager.
3. Build and push the Docker image: `docker build -t ecovision-ai-backend .`
4. Run database migrations: `alembic upgrade head` (the provided `docker-compose.yml`
   does this automatically on container start).
5. (Optional) Mount or bake in a fine-tuned `YOLO_MODEL_PATH` for real pollution
   detection, and run `python ml/train.py` against real historical sensor data for
   a production-quality AQI model.
6. Front the backend with a reverse proxy / load balancer (e.g. Nginx, an ALB) for
   TLS termination, and persist `app/uploads/` to durable storage (e.g. an S3-backed
   volume) in multi-instance deployments.
