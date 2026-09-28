from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service
from app.schemas import ServiceCreate, ServiceResponse

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=List[ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    """Retrieve all monitored services."""
    return db.query(Service).order_by(Service.name.asc()).all()


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    """Register a new service."""
    existing = db.query(Service).filter(Service.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Service with name '{payload.name}' already exists.",
        )

    service = Service(name=payload.name, url=payload.url)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service
