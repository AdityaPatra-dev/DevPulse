from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


# --- Service Schemas ---
class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Authentication Service"])
    url: Optional[str] = Field(None, max_length=255, examples=["https://auth.internal.example.com"])


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Incident Schemas ---
class IncidentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, examples=["High latency on login API"])
    severity: str = Field(default="medium", examples=["low", "medium", "high", "critical"])
    status: str = Field(default="investigating", examples=["investigating", "identified", "monitoring", "resolved"])


class IncidentCreate(IncidentBase):
    service_id: int = Field(..., examples=[1])


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    severity: Optional[str] = Field(None, examples=["low", "medium", "high", "critical"])
    status: Optional[str] = Field(None, examples=["investigating", "identified", "monitoring", "resolved"])


class IncidentResponse(IncidentBase):
    id: int
    service_id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ServiceWithIncidents(ServiceResponse):
    incidents: List[IncidentResponse] = []


# --- Health Schema ---
class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime
