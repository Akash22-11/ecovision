"""
EcoVision AI - FastAPI application entrypoint.

"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError
from pydantic import ValidationError as PydanticValidationError

from app.config import settings
from app.routes import auth, dashboard, hotspots, municipality, prediction, reports, weather, ai
from app.utils.logger import logger
from app.utils.validators import ValidationError


# --- Lifecycle ---------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup code goes here ---
    # TODO: paste whatever was in your old @app.on_event("startup") function here
    # (e.g. creating DB tables, loading the YOLOv8 model, warming up the AQI predictor)
    yield
    # --- shutdown code goes here (if you had @app.on_event("shutdown") too) ---


# --- App instance --------------------------------------------------------------------

app = FastAPI(
    title="EcoVision AI",
    description="Pollution monitoring API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = settings.API_V1_PREFIX
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(weather.router, prefix=API_PREFIX)
app.include_router(hotspots.router, prefix=API_PREFIX)
app.include_router(prediction.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(municipality.router, prefix=API_PREFIX)
app.include_router(ai.router, prefix=API_PREFIX)

# --- Global exception handlers ----------------------------------------------------


@app.exception_handler(ValidationError)
async def domain_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handles our domain-level ValidationError (400/401/403/404/409 as set by the raiser)."""
    logger.warning(f"ValidationError on {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(PydanticValidationError)
async def pydantic_validation_exception_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    logger.warning(f"Pydantic validation error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})


@app.exception_handler(JWTError)
async def jwt_exception_handler(request: Request, exc: JWTError) -> JSONResponse:
    logger.warning(f"JWT error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid or expired token."})


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


# --- Health check routes ------------------------------------------------------------


@app.get("/", tags=["Health"], summary="Health check")
async def root() -> dict:
    return {"status": "ok", "service": settings.APP_NAME, "version": "1.0.0"}


@app.get("/health", tags=["Health"], summary="Health check")
async def health() -> dict:
    return {"status": "healthy"}
