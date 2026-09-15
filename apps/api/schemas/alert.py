"""Alert Schemas."""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class AlertBase(BaseModel):
    event_id: str
    camera_id: str
    watchlist_entry_id: Optional[str] = None
    severity: str  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    title: str
    description: str
    matched_entity: str
    match_confidence: float
    latitude: float
    longitude: float
    evidence_frame_uri: Optional[str] = None
    evidence_crop_uri: Optional[str] = None
    status: str = "NEW"  # NEW, ACKNOWLEDGED, ESCALATED, RESOLVED, FALSE_POSITIVE
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    acknowledged_by: Optional[str] = None


class AlertOut(AlertBase):
    id: str
    camera_name: Optional[str] = None
    district: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertStatsOut(BaseModel):
    total_active: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    acknowledged_count: int
    severity_breakdown: Dict[str, int]
