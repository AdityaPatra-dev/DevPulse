from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/healthz", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Database-backed healthcheck endpoint."""
    try:
        # Executes lightweight query to verify active database connectivity
        db.execute(text("SELECT 1"))
        return HealthResponse(
            status="healthy",
            database="connected",
            timestamp=datetime.now(timezone.utc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unreachable: {str(exc)}",
        )
