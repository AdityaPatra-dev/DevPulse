import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.metrics import PrometheusMiddleware, metrics_endpoint
from app.routes import services, incidents, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle context to initialize database schema."""
    try:
        # Ensure database tables exist upon application launch
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(f"Warning: Database schema initialization deferred/skipped: {exc}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="DevPulse — Cloud Incident & Service Status Tracker",
    version="1.0.0",
    lifespan=lifespan,
)

# Custom metrics middleware for Prometheus (Track B)
app.add_middleware(PrometheusMiddleware)

# API Routers
app.include_router(health.router)
app.include_router(services.router)
app.include_router(incidents.router)

# Metrics endpoint for Prometheus scraper
app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], tags=["Observability"])

# Static Files & Dashboard UI
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", tags=["Frontend"])
async def serve_index():
    """Serve the root dashboard user interface."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "DevPulse API is running. Static assets missing."}
