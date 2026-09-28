from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Incident, Service
from app.schemas import IncidentCreate, IncidentResponse, IncidentUpdate

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=List[IncidentResponse])
def get_incidents(
    status: Optional[str] = Query(None, description="Filter by status (investigating, identified, monitoring, resolved)"),
    service_id: Optional[int] = Query(None, description="Filter by service ID"),
    db: Session = Depends(get_db),
):
    """List incidents with optional filters."""
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if service_id:
        query = query.filter(Incident.service_id == service_id)
    return query.order_by(Incident.created_at.desc()).all()


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    """Create a new incident for an existing service."""
    service = db.query(Service).filter(Service.id == payload.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with id {payload.service_id} does not exist.",
        )

    incident = Incident(
        service_id=payload.service_id,
        title=payload.title,
        severity=payload.severity,
        status=payload.status,
    )
    if payload.status == "resolved":
        incident.resolved_at = datetime.now(timezone.utc)

    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db)):
    """Update status, severity, or title of an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with id {incident_id} not found.",
        )

    if payload.title is not None:
        incident.title = payload.title
    if payload.severity is not None:
        incident.severity = payload.severity
    if payload.status is not None:
        incident.status = payload.status
        if payload.status == "resolved" and incident.resolved_at is None:
            incident.resolved_at = datetime.now(timezone.utc)
        elif payload.status != "resolved":
            incident.resolved_at = None

    db.commit()
    db.refresh(incident)
    return incident
