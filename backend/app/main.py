"""
CampusIQ FastAPI Backend
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, SessionLocal, Base

# Import models so SQLAlchemy registers them before create_all
from app.models import (  # noqa: F401
    Student, Department, Achievement, StridePoint, Report, UploadedFile, AdminProfile
)

from app.routes import (
    health,
    dashboard,
    students,
    academics,
    attendance,
    placements,
    departments,
    achievements,
    stride_points,
    upload,
    reports,
    settings as settings_route,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified.")

    # Seed with sample data if empty
    from app.utils.seeder import seed_database
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title="CampusIQ API",
    description="Backend API for the CampusIQ Student & Campus Analytics Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error at %s: %s", request.url, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check the server logs."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(students.router, prefix="/api", tags=["Students"])
app.include_router(academics.router, prefix="/api", tags=["Academics"])
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])
app.include_router(placements.router, prefix="/api", tags=["Placements"])
app.include_router(departments.router, prefix="/api", tags=["Departments"])
app.include_router(achievements.router, prefix="/api", tags=["Achievements"])
app.include_router(stride_points.router, prefix="/api", tags=["Stride Points"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(settings_route.router, prefix="/api", tags=["Settings"])

# ── Root redirect ─────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    return {"message": "CampusIQ API is running. Visit /docs for API documentation."}
