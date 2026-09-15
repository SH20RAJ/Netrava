"""Investigation & Dossier Schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from schemas.vehicle import SightingOut


class InvestigationEventOut(BaseModel):
    sighting_id: str
    relevance_notes: Optional[str] = None
    added_at: datetime
    sighting: Optional[SightingOut] = None


class InvestigationBase(BaseModel):
    case_number: str
    title: str
    lead_investigator: str
    department: str = "Gujarat Police CID Crime"
    target_plate: Optional[str] = None
    status: str = "OPEN"
    summary: Optional[str] = None


class InvestigationCreate(InvestigationBase):
    pass


class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    lead_investigator: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None


class InvestigationOut(InvestigationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    events: List[InvestigationEventOut] = []

    class Config:
        from_attributes = True
